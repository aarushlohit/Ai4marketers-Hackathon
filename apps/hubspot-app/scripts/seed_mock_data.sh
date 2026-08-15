#!/bin/bash
# Mock Contacts
contacts=(
  '{"properties": {"email": "alice@example.com", "firstname": "Alice", "lastname": "Smith", "company": "Acme Corp"}}'
  '{"properties": {"email": "bob@example.com", "firstname": "Bob", "lastname": "Jones", "company": "Globex"}}'
  '{"properties": {"email": "charlie@example.com", "firstname": "Charlie", "lastname": "Brown", "company": "Initech"}}'
  '{"properties": {"email": "diana@example.com", "firstname": "Diana", "lastname": "Prince", "company": "Wayne Ent"}}'
)

echo "🌱 Seeding mock data to HubSpot..."
for contact in "${contacts[@]}"; do
  echo "Creating contact: $contact"
  hs api /crm/v3/objects/contacts -X POST --data "$contact"
done
echo "🎉 Done seeding mock data!"
