#!/usr/bin/env python3

import grpc
from concurrent import futures
import sys
import os
import time
import pickle
import base64
import psutil
from datetime import datetime

sys.path.insert(0, '/opt/cpr/app/proto')

import auth_pb2
import auth_pb2_grpc
import user_pb2
import user_pb2_grpc
import backup_pb2
import backup_pb2_grpc
import monitoring_pb2
import monitoring_pb2_grpc

# Import database module
import database

# Service start time for uptime calculation
SERVICE_START_TIME = time.time()

# Flag for admin users
FLAG_1 = "H7CTF{d1d_y0u_l3arn_ab0ut_pr0t0buf_inject10ns}"


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
    """Authentication service implementation"""
    
    def RegisterUser(self, request, context):
        """Register a new user"""
        
        if not request.username or not request.email or not request.password:
            return auth_pb2.RegisterResponse(
                success=False,
                message="All fields are required"
            )
        
        success, message, user_id = database.register_user(
            request.username,
            request.email,
            request.password
        )
        
        return auth_pb2.RegisterResponse(
            success=success,
            message=message,
            user_id=user_id if user_id else ""
        )
    
    def LoginUser(self, request, context):
        """Authenticate user"""
        
        success, message, user_id = database.authenticate_user(
            request.username,
            request.password
        )
        
        return auth_pb2.LoginResponse(
            success=success,
            message=message,
            user_id=user_id if user_id else ""
        )


class UserServicer(user_pb2_grpc.UserServiceServicer):
    """User management service implementation"""
    
    def GetUserDetails(self, request, context):
        """Get user details"""
        
        user = database.get_user_details(request.user_id)
        
        if not user:
            return user_pb2.UserResponse(
                success=False,
                user_id=request.user_id
            )
        
        # Determine role
        role = "admin" if user['is_admin'] else "user"
        
        token = FLAG_1 if user['is_admin'] else ""
        
        return user_pb2.UserResponse(
            success=True,
            user_id=user['user_id'],
            username=user['username'],
            email=user['email'],
            bio=user['bio'],
            role=role,
            privilege_level=user['privilege_level'],
            token=token
        )
    
    def UpdateProfile(self, request, context):
        """Update user profile information"""
        
        # Extract fields from request
        name = request.name if request.name else None
        email = request.email if request.email else None
        bio = request.bio if request.bio else None
        is_admin = request.is_admin
        privilege_level = request.privilege_level
        
        # Update database with provided fields
        success, message = database.update_user_profile(
            request.user_id,
            name=name,
            email=email,
            bio=bio,
            is_admin=is_admin if is_admin else None,
            privilege_level=privilege_level if privilege_level > 0 else None
        )
        
        return user_pb2.UpdateProfileResponse(
            success=success,
            message=message
        )
    
    def ListUsers(self, request, context):
        """List all users (admin only)"""
        
        # Check admin privileges
        if not database.is_user_admin(request.user_id):
            return user_pb2.ListUsersResponse(
                success=False,
                users=[]
            )
        
        users = database.list_all_users()
        
        user_infos = []
        for user in users:
            user_infos.append(user_pb2.UserInfo(
                user_id=user['user_id'],
                username=user['username'],
                email=user['email'],
                role=user['role']
            ))
        
        return user_pb2.ListUsersResponse(
            success=True,
            users=user_infos
        )


class BackupServicer(backup_pb2_grpc.BackupServiceServicer):
    """Backup service for data management"""
    
    def CreateBackup(self, request, context):
        """Create a backup (admin only)"""
        
        # Check admin privileges
        if not database.is_user_admin(request.user_id):
            return backup_pb2.BackupResponse(
                success=False,
                message="Admin privileges required"
            )
        
        backup_id = f"backup_{int(time.time())}"
        
        return backup_pb2.BackupResponse(
            success=True,
            message="Backup created successfully",
            backup_id=backup_id
        )
    
    def RestoreBackup(self, request, context):
        """Restore backup from serialized data"""
        
        # Check admin privileges
        if not database.is_user_admin(request.user_id):
            return backup_pb2.RestoreResponse(
                success=False,
                message="Admin privileges required"
            )
        
        try:
            backup_data = request.backup_data
            
            if backup_data:
                # Deserialize backup data
                deserialized = pickle.loads(backup_data)
                
                return backup_pb2.RestoreResponse(
                    success=True,
                    message="Backup restored successfully"
                )
            else:
                return backup_pb2.RestoreResponse(
                    success=False,
                    message="No backup data provided"
                )
        
        except Exception as e:
            return backup_pb2.RestoreResponse(
                success=False,
                message=f"Restore failed: {str(e)}"
            )
    
    def ListBackups(self, request, context):
        """List available backups (admin only)"""
        
        # Check admin privileges
        if not database.is_user_admin(request.user_id):
            return backup_pb2.ListBackupsResponse(
                success=False,
                backups=[]
            )
        
        backups = [
            backup_pb2.BackupInfo(
                backup_id="backup_001",
                backup_name="system_backup_2025_10_01",
                created_at="2025-10-01 10:00:00",
                size=1024000
            ),
            backup_pb2.BackupInfo(
                backup_id="backup_002",
                backup_name="user_data_2025_10_15",
                created_at="2025-10-15 14:30:00",
                size=2048000
            )
        ]
        
        return backup_pb2.ListBackupsResponse(
            success=True,
            backups=backups
        )


class MetricsServicer(monitoring_pb2_grpc.MetricsServiceServicer):
    """System monitoring and metrics collection service"""
    
    def GetSystemMetrics(self, request, context):
        """Get system metrics"""
        
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        uptime = int(time.time() - SERVICE_START_TIME)
        
        metrics = monitoring_pb2.SystemMetrics(
            cpu_usage=cpu,
            memory_usage=memory,
            uptime_seconds=uptime,
            active_connections=4
        )
        
        return monitoring_pb2.MetricsResponse(
            success=True,
            metrics=metrics
        )
    
    def GetServiceHealth(self, request, context):
        """Get service health status"""
        
        services = [
            monitoring_pb2.ServiceStatus(
                service_name="cpr.auth.AuthService",
                status="healthy",
                uptime=int(time.time() - SERVICE_START_TIME)
            ),
            monitoring_pb2.ServiceStatus(
                service_name="cpr.user.UserService",
                status="healthy",
                uptime=int(time.time() - SERVICE_START_TIME)
            ),
            monitoring_pb2.ServiceStatus(
                service_name="cpr.backup.BackupService",
                status="healthy",
                uptime=int(time.time() - SERVICE_START_TIME)
            )
        ]
        
        return monitoring_pb2.HealthResponse(
            success=True,
            services=services
        )
    
    def ListEndpoints(self, request, context):
        """List available endpoints"""
        
        endpoints = [
            monitoring_pb2.Endpoint(
                service="cpr.auth.AuthService",
                method="RegisterUser",
                description="Register a new user account"
            ),
            monitoring_pb2.Endpoint(
                service="cpr.auth.AuthService",
                method="LoginUser",
                description="Authenticate user credentials"
            ),
            monitoring_pb2.Endpoint(
                service="cpr.user.UserService",
                method="GetUserDetails",
                description="Retrieve user information"
            ),
            monitoring_pb2.Endpoint(
                service="cpr.user.UserService",
                method="UpdateProfile",
                description="Update user profile data"
            ),
            monitoring_pb2.Endpoint(
                service="cpr.backup.BackupService",
                method="RestoreBackup",
                description="Restore system backup (admin)"
            )
        ]
        
        return monitoring_pb2.EndpointsResponse(
            success=True,
            endpoints=endpoints
        )


def serve():
    """Start the gRPC server"""
    
    # Initialize database
    database.init_database()
    
    # Create server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add services
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServicer(), server)
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(), server)
    backup_pb2_grpc.add_BackupServiceServicer_to_server(BackupServicer(), server)
    monitoring_pb2_grpc.add_MetricsServiceServicer_to_server(MetricsServicer(), server)
    
    # Reflection disabled for production
    # from grpc_reflection.v1alpha import reflection
    # SERVICE_NAMES = (
    #     auth_pb2.DESCRIPTOR.services_by_name['AuthService'].full_name,
    #     user_pb2.DESCRIPTOR.services_by_name['UserService'].full_name,
    #     backup_pb2.DESCRIPTOR.services_by_name['BackupService'].full_name,
    #     monitoring_pb2.DESCRIPTOR.services_by_name['MetricsService'].full_name,
    #     reflection.SERVICE_NAME,
    # )
    # reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # Start server
    server.add_insecure_port('[::]:50051')
    server.start()
    
    print("[*] CPR Runtime gRPC Server started on port 50051")
    print("[*] Services: Auth, User, Backup, Monitoring")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[*] Shutting down server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
