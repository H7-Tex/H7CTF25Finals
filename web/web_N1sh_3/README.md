# build
docker build -t web_n1sh_3:latest .
docker run -d --name web_n1sh_3_challenge -p 3000:3000 web_n1sh_3:latest