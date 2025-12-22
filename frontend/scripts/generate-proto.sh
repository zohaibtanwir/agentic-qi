#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

PROTO_DIR="../protos"
OUT_DIR="./lib/grpc/generated"

echo "Generating TypeScript code from proto files..."

# Create output directory
mkdir -p $OUT_DIR

# Generate TypeScript code using ts-proto
protoc \
  --plugin=./node_modules/.bin/protoc-gen-ts_proto \
  --ts_proto_out=$OUT_DIR \
  --ts_proto_opt=outputServices=nice-grpc,outputServices=generic-definitions,useExactTypes=false,esModuleInterop=true \
  -I=$PROTO_DIR \
  test_cases.proto

echo "✓ Proto files generated successfully!"
echo "  Output: $OUT_DIR/"
ls -lh $OUT_DIR/
