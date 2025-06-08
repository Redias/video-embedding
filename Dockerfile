FROM python:3.10.18

COPY service /workspace

WORKDIR /workspace

ENV PYTHONPATH=/workspace

RUN echo \
    && sed -i 's|archive.ubuntu.com|mirrors.aliyun.com|g' /etc/apt/sources.list \
    && sed -i 's|security.ubuntu.com|mirrors.aliyun.com|g' /etc/apt/sources.list \
    && apt update \
    # set locale
    && apt install -y locales \
    && locale-gen zh_CN.UTF-8 \
    && echo

ENV LANG=zh_CN.UTF-8 \
    LANGUAGE=zh_CN:zh \
    LC_ALL=zh_CN.UTF-8

RUN echo \
    && pip install -r /workspace/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com --no-cache-dir \
    # clear cache
    && apt clean \
    && apt autoclean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache \
    && find /workspace -type d -name "__pycache__" -exec rm -rf {} + \
    && echo

ENTRYPOINT [ "/bin/bash", "-l", "-c" ]
