FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy remaining files
COPY . .

# Build the Next.js app
RUN npm run build

# Railway automatically sets the PORT environment variable
ENV PORT=3000
EXPOSE 3000

CMD ["npm", "start"]
