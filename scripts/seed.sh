#!/bin/bash
set -e

echo "Seeding development data..."
python -m app.db.seed
echo "Seed complete."
