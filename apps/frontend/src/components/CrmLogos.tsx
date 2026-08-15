import React from "react";

export type CRMType = "salesforce" | "zoho" | "hubspot" | "dynamics" | "pipedrive";

// Keep provider marks as local SVGs so the marketplace never falls back to
// emoji or depends on a third-party image host during deployment.

export function SalesforceLogo({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M19.1 9.4c-.6-2.5-2.8-4.4-5.5-4.4-1.9 0-3.6.9-4.7 2.3-1.1-.7-2.4-1.1-3.8-1.1-3.6 0-6.6 2.8-6.9 6.4C-1.8 15.3 0 19 3.5 19c.6 0 1.2-.1 1.7-.2 1 1 2.4 1.7 4 1.7 2 0 3.8-1.1 4.8-2.7.7.3 1.5.5 2.3.5 3.3 0 6-2.7 6-6 0-1.1-.3-2.1-.9-3z"
        fill="#00A1E0"
      />
    </svg>
  );
}

export function HubspotLogo({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M18.8 10.9V7.7l2.2-1.3-1.2-2.1-2.2 1.3V3.1h-2.5v2.5L12.9 4.3l-1.2 2.1 2.2 1.3v3.2c-1.3.6-2.2 1.9-2.2 3.4 0 2.1 1.7 3.8 3.8 3.8s3.8-1.7 3.8-3.8c0-1.5-.9-2.8-2.2-3.4zm-1.6 5.2c-1 0-1.8-.8-1.8-1.8s.8-1.8 1.8-1.8 1.8.8 1.8 1.8-.8 1.8-1.8 1.8zM5.2 12c0-3.7 3-6.8 6.8-6.8h.5V2.6h-.5C6.4 2.6 2.6 6.4 2.6 12s3.8 9.4 9.4 9.4h.5v-2.6h-.5C8.2 18.8 5.2 15.7 5.2 12z"
        fill="#FF7A59"
      />
    </svg>
  );
}

export function ZohoLogo({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="4" width="9" height="7" rx="1.5" fill="#E42528" />
      <rect x="13" y="4" width="9" height="7" rx="1.5" fill="#2BA84A" />
      <rect x="2" y="13" width="9" height="7" rx="1.5" fill="#1565C0" />
      <rect x="13" y="13" width="9" height="7" rx="1.5" fill="#F2A900" />
    </svg>
  );
}

export function DynamicsLogo({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="2" width="9.5" height="9.5" fill="#F25022" />
      <rect x="12.5" y="2" width="9.5" height="9.5" fill="#7FBA00" />
      <rect x="2" y="12.5" width="9.5" height="9.5" fill="#00A4EF" />
      <rect x="12.5" y="12.5" width="9.5" height="9.5" fill="#FFB900" />
    </svg>
  );
}

export function PipedriveLogo({ className = "h-6 w-6" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" fill="#28A745" />
      <path d="M8.5 7h4a3.5 3.5 0 0 1 0 7H11v3H8.5V7zm2.5 4.5h1.5a1 1 0 0 0 0-2H11v2z" fill="#FFFFFF" />
    </svg>
  );
}

export function CrmLogo({ type, className = "h-6 w-6" }: { type: CRMType; className?: string }) {
  switch (type) {
    case "salesforce":
      return <SalesforceLogo className={className} />;
    case "hubspot":
      return <HubspotLogo className={className} />;
    case "zoho":
      return <ZohoLogo className={className} />;
    case "dynamics":
      return <DynamicsLogo className={className} />;
    case "pipedrive":
      return <PipedriveLogo className={className} />;
    default:
      return null;
  }
}
