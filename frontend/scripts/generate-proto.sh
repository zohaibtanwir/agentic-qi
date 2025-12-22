#!/bin/bash

set -e

PROTO_DIR="../protos"
OUT_DIR="./lib/grpc/generated"

echo "Generating TypeScript code from proto files..."

# Create output directory
mkdir -p $OUT_DIR

# Generate JavaScript/TypeScript code
protoc \
  -I=$PROTO_DIR \
  test_cases.proto \
  --js_out=import_style=commonjs,binary:$OUT_DIR \
  --grpc-web_out=import_style=typescript,mode=grpcwebtext:$OUT_DIR

echo "✓ Proto files generated successfully!"
echo "  Output: $OUT_DIR/"
ls -lh $OUT_DIR/
