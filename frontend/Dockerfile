FROM node:18-alpine

WORKDIR /app

# package.json과 package-lock.json만 먼저 복사
COPY package*.json ./

# 모든 의존성 설치 (development 포함)
RUN npm install

# 소스 코드 복사
COPY . .

# 환경 변수 설정
ENV VITE_API_URL=http://localhost:8000

# 개발 서버 실행
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
