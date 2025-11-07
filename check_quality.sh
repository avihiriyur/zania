#!/bin/bash

# Code Quality Check Script
# Run this to check code quality before committing

echo "🔍 Running code quality checks..."
echo ""

# Activate virtual environment
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv activate myenv

echo "📝 Running Black (code formatter)..."
black --check app/ tests/ --line-length=127
BLACK_EXIT=$?

echo ""
echo "🔎 Running Flake8 (linter)..."
flake8 app/ tests/ --config=.flake8
FLAKE8_EXIT=$?

echo ""
echo "✅ Running Pytest (tests)..."
pytest tests/ -v
PYTEST_EXIT=$?

echo ""
echo "📊 Summary:"
if [ $BLACK_EXIT -eq 0 ] && [ $FLAKE8_EXIT -eq 0 ] && [ $PYTEST_EXIT -eq 0 ]; then
    echo "✅ All checks passed!"
    exit 0
else
    echo "❌ Some checks failed. Please fix the issues above."
    exit 1
fi

