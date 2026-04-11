# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

# Multi-stage build using openenv-base
# This Dockerfile is flexible and works for both:
# - In-repo environments (with local OpenEnv sources)
# - Standalone environments (with openenv from PyPI/Git)
# The build script (openenv build) handles context detection and sets appropriate build args.

# Use OpenEnv base image
FROM ghcr.io/meta-pytorch/openenv-base:latest

WORKDIR /app/env

# Copy all files
COPY . /app/env

# Install dependencies using pip (not uv)
RUN pip install --no-cache-dir \
    openenv-core>=0.2.2 \
    fastapi>=0.115.0 \
    "uvicorn[standard]>=0.32.0" \
    pydantic>=2.0.0 \
    openai>=1.0.0

# Set environment
ENV PYTHONPATH="/app/env:$PYTHONPATH"

# Expose port
EXPOSE 7860

# Run server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]