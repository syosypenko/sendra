#!/bin/bash

echo "Running Backend Tests (Collections API)..."
cd backend
pip install pytest pytest-asyncio -q
python -m pytest test_collections.py -v

if [ $? -eq 0 ]; then
  echo "✅ Backend tests passed"
else
  echo "❌ Backend tests failed"
  exit 1
fi

echo ""
echo "Running Frontend Tests (Collections Service)..."
cd ../frontend
npm test -- frontend/src/services/__tests__/api.collections.test.js --watchAll=false

if [ $? -eq 0 ]; then
  echo "✅ Frontend tests passed"
else
  echo "❌ Frontend tests failed"
  exit 1
fi

echo ""
echo "✅ All tests passed!"
