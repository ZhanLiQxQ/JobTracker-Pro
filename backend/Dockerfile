# --- Build Stage ---
# Use official Maven image as build environment, includes Java 17
FROM maven:3.9.6-eclipse-temurin-17-focal AS build

# Set working directory
WORKDIR /app

# Copy pom.xml file and download dependencies to leverage Docker layer caching
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy all source code
COPY src ./src

# Package application into jar file, skip tests
RUN mvn package -DskipTests

# --- Run Stage ---
# Use lightweight OpenJDK image as runtime environment
FROM openjdk:17-jdk-slim

# Set working directory
WORKDIR /app

# Copy packaged jar file from build stage
COPY --from=build /app/target/*.jar app.jar

# Expose port for backend application
EXPOSE 8080

# Run jar file when container starts
# Pass SPRING_PROFILES_ACTIVE=prod to activate production environment configuration
ENTRYPOINT ["java", "-Dspring.profiles.active=prod", "-jar", "app.jar"]
