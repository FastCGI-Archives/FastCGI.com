FROM alpine:3.8
ENV LC_ALL C.UTF-8
RUN apk add python3 wget && \
    adduser -D user
USER user
WORKDIR /home/user
COPY --chown=user:user nuke.sh rebuild.sh wayback-helper.py ./
RUN ./rebuild.sh
