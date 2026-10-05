FROM --platform=linux/amd64 nvidia/cuda@sha256:6617a625f4090c76c545a0e7d63f2e441718ef9af7f4efe7dd1242a29e289fd7
ARG TORCH_CUDA_ARCH_LIST
ARG BUILD_RECIPE_BINDING
ENV DEBIAN_FRONTEND=noninteractive SOURCE_DATE_EPOCH=1712707200 TZ=UTC LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
COPY . /opt/qwen-bundle/
WORKDIR /opt/qwen-bundle
RUN sha256sum -c inputs.sha256
RUN test -n "$TORCH_CUDA_ARCH_LIST" && test -n "$BUILD_RECIPE_BINDING" && bash build/install_apt.sh
RUN mkdir /opt/cpython-src && tar -xzf archives/cpython.tar.gz -C /opt/cpython-src --strip-components=1 && cd /opt/cpython-src && CC=gcc-10 CXX=g++-10 ./configure --prefix=/opt/python3.11.9 --with-ensurepip=no --disable-shared && make -j2 && make install
ENV PATH=/opt/python3.11.9/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin PYTHONPATH=/opt/qwen-bundle PIP_NO_INDEX=1 PIP_DISABLE_PIP_VERSION_CHECK=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
RUN PYTHONPATH=/opt/qwen-bundle/wheelhouse/pip-25.0.1-py3-none-any.whl /opt/python3.11.9/bin/python3.11 -B -m pip install --no-index --no-deps /opt/qwen-bundle/wheelhouse/pip-25.0.1-py3-none-any.whl
RUN python3.11 -B -m pip install --no-index --find-links=wheelhouse --require-hashes --no-deps -r requirements-linux-cp311.lock
ENV CC=gcc-10 CXX=g++-10 VLLM_TARGET_DEVICE=cuda VLLM_VERSION_OVERRIDE=0.11.2 VLLM_USE_PRECOMPILED=0 VLLM_CUTLASS_SRC_DIR=/opt/build-sources/cutlass VLLM_FLASH_ATTN_SRC_DIR=/opt/build-sources/vllm-flash-attention MAX_JOBS=2 NVCC_THREADS=1 CMAKE_BUILD_TYPE=Release TORCH_CUDA_ARCH_LIST=${TORCH_CUDA_ARCH_LIST}
RUN python3.11 -B build/prepare_sources.py && python3.11 -B -m pip wheel --no-index --no-deps --no-build-isolation --wheel-dir=/opt/built-wheels /opt/build-sources/transformers /opt/build-sources/peft /opt/build-sources/vllm && python3.11 -B -m pip install --no-index --no-deps /opt/built-wheels/*.whl && python3.11 -B -m pip check
RUN mkdir /opt/build-evidence && python3.11 -B build/runtime_self_test.py --output=/opt/build-evidence/self_test.json && python3.11 -B build/sbom.py --output=/opt/build-evidence/sbom.json
LABEL org.qwen30.governance="frozen-8K-B.1G2A-0" org.qwen30.model-free-build="true"
USER 65532:65532
ENTRYPOINT []
CMD ["/opt/python3.11.9/bin/python3.11", "-B", "/opt/qwen-bundle/build/runtime_self_test.py"]
