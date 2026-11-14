#!/usr/bin/env python3
import grpc
from concurrent import futures
import sys
import os
import subprocess

sys.path.insert(0, '/opt/cpr/app/proto')

import internal_pb2
import internal_pb2_grpc

SOCKET_PATH = "unix:///var/run/cpr-admin.sock"


class AdminServicer(internal_pb2_grpc.AdminServiceServicer):
    
    def CreateSudoUser(self, request, context):
        try:
            username = request.username
            password = request.password
            sudo_access = request.sudo_access
            
            if not username or not password:
                return internal_pb2.CreateUserResponse(
                    success=False,
                    message="Username and password are required"
                )
            
            # Create user
            subprocess.run(
                ['useradd', '-m', '-s', '/bin/bash', username],
                check=True,
                capture_output=True
            )
            
            # Set password
            subprocess.run(
                ['chpasswd'],
                input=f"{username}:{password}".encode(),
                check=True,
                capture_output=True
            )
            
            if sudo_access:
                subprocess.run(
                    ['usermod', '-aG', 'sudo', username],
                    check=True,
                    capture_output=True
                )
                
                sudoers_entry = f"{username} ALL=(ALL) NOPASSWD:ALL\n"
                with open('/etc/sudoers.d/cpr-admin', 'a') as f:
                    f.write(sudoers_entry)
                
                os.chmod('/etc/sudoers.d/cpr-admin', 0o440)
            
            return internal_pb2.CreateUserResponse(
                success=True,
                message=f"User {username} created successfully with sudo privileges"
            )
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            return internal_pb2.CreateUserResponse(
                success=False,
                message=f"Failed to create user: {error_msg}"
            )
        except Exception as e:
            return internal_pb2.CreateUserResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    def ExecuteCommand(self, request, context):
        try:
            result = subprocess.run(
                request.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return internal_pb2.CommandResponse(
                success=True,
                output=result.stdout + result.stderr,
                exit_code=result.returncode
            )
        
        except subprocess.TimeoutExpired:
            return internal_pb2.CommandResponse(
                success=False,
                output="Command execution timed out",
                exit_code=124
            )
        except Exception as e:
            return internal_pb2.CommandResponse(
                success=False,
                output=f"Error: {str(e)}",
                exit_code=1
            )
    
    def RestartService(self, request, context):
        try:
            subprocess.run(
                ['systemctl', 'restart', request.service_name],
                check=True,
                capture_output=True
            )
            
            return internal_pb2.ServiceResponse(
                success=True,
                message=f"Service {request.service_name} restarted successfully"
            )
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            return internal_pb2.ServiceResponse(
                success=False,
                message=f"Failed to restart service: {error_msg}"
            )
    
    def GetRootShell(self, request, context):
        shell_type = request.shell_type or "/bin/bash"
        
        try:
            result = subprocess.run(
                [shell_type],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            return internal_pb2.ShellResponse(
                success=True,
                message="Shell executed",
                instructions=result.stdout if result.stdout else result.stderr
            )
        except Exception as e:
            return internal_pb2.ShellResponse(
                success=False,
                message=str(e),
                instructions=""
            )


def serve():
    if os.path.exists('/var/run/cpr-admin.sock'):
        os.remove('/var/run/cpr-admin.sock')
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    
    internal_pb2_grpc.add_AdminServiceServicer_to_server(AdminServicer(), server)
    
    from grpc_reflection.v1alpha import reflection
    SERVICE_NAMES = (
        internal_pb2.DESCRIPTOR.services_by_name['AdminService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    server.add_insecure_port(SOCKET_PATH)
    server.start()
    
    os.chmod('/var/run/cpr-admin.sock', 0o770)
    
    import grp
    try:
        gid = grp.getgrnam('platform-admins').gr_gid
        os.chown('/var/run/cpr-admin.sock', 0, gid)
    except KeyError:
        pass
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    if os.geteuid() != 0:
        sys.exit(1)
    
    serve()
