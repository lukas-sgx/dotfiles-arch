# Dockerfile : Jenkins on Ubuntu 24.04
# Base image: ubuntu:24.04
# Installs OpenJDK 17, adds the Jenkins apt repository and installs Jenkins.
# Runs Jenkins by launching the jenkins.war directly (no systemd).

FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ENV JENKINS_HOME=/var/lib/jenkins
ENV JAVA_OPTS="-Djava.awt.headless=true"

# Install required packages, Java and add Jenkins repository (modern, signed-by approach)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates curl gnupg2 lsb-release openjdk-17-jdk \
    && mkdir -p /usr/share/keyrings \
    && curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | gpg --dearmor -o /usr/share/keyrings/jenkins-jenkinsio-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/jenkins-jenkinsio-keyring.gpg] https://pkg.jenkins.io/debian-stable binary/" > /etc/apt/sources.list.d/jenkins.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends jenkins \
    && rm -rf /var/lib/apt/lists/*

# Expose Jenkins ports
EXPOSE 8080 50000

# Persist Jenkins data
VOLUME ["/var/lib/jenkins"]

# Ensure jenkins user owns the home directories (package usually creates user)
RUN chown -R jenkins:jenkins /var/lib/jenkins /var/cache/jenkins /var/log/jenkins || true

# Run as the 'jenkins' user
USER jenkins

# Start Jenkins by running the installed war file directly
# You can override JAVA_OPTS and other args at runtime if needed
CMD ["java", "-jar", "/usr/share/java/jenkins.war"]
