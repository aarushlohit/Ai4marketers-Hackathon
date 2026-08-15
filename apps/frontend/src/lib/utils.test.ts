/**
 * Unit tests for utility functions.
 */
import {
  cn,
  formatCurrency,
  formatPercent,
  truncate,
  getInitials,
  getFirstNameInitial,
} from "./utils";

describe("cn (class merging)", () => {
  it("merges classes", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("resolves Tailwind conflicts (last wins)", () => {
    // tailwind-merge should keep the last conflicting class
    const result = cn("text-red-500", "text-blue-500");
    expect(result).toBe("text-blue-500");
  });

  it("handles conditional classes", () => {
    const result = cn("base", false && "no", true && "yes");
    expect(result).toBe("base yes");
  });

  it("ignores undefined and null", () => {
    expect(cn("a", undefined, null as unknown as string, "b")).toBe("a b");
  });
});

describe("formatCurrency", () => {
  it("formats USD with no decimals", () => {
    expect(formatCurrency(1000)).toBe("$1,000");
  });

  it("formats large numbers with commas", () => {
    expect(formatCurrency(1250000)).toBe("$1,250,000");
  });

  it("formats zero", () => {
    expect(formatCurrency(0)).toBe("$0");
  });
});

describe("formatPercent", () => {
  it("converts 0.85 to 85.0%", () => {
    expect(formatPercent(0.85)).toBe("85.0%");
  });

  it("respects custom decimal places", () => {
    expect(formatPercent(0.333, 2)).toBe("33.30%");
  });

  it("handles 0", () => {
    expect(formatPercent(0)).toBe("0.0%");
  });

  it("handles 1 (100%)", () => {
    expect(formatPercent(1)).toBe("100.0%");
  });
});

describe("truncate", () => {
  it("truncates long strings", () => {
    expect(truncate("Hello World", 5)).toBe("Hello…");
  });

  it("does not truncate short strings", () => {
    expect(truncate("Hi", 10)).toBe("Hi");
  });

  it("truncates at exact boundary", () => {
    // "Hello" is 5 chars — maxLength=5 means no truncation
    expect(truncate("Hello", 5)).toBe("Hello");
  });
});

describe("getInitials", () => {
  it("returns initials for full name", () => {
    expect(getInitials("Jane Doe")).toBe("JD");
  });

  it("handles single name", () => {
    expect(getInitials("Alice")).toBe("A");
  });

  it("caps at 2 chars", () => {
    expect(getInitials("John Michael Smith")).toBe("JM");
  });

  it("uppercases initials", () => {
    expect(getInitials("alice brown")).toBe("AB");
  });
});

describe("getFirstNameInitial", () => {
  it("returns first letter of first name", () => {
    expect(getFirstNameInitial("Jane")).toBe("J");
  });

  it("uppercases the letter", () => {
    expect(getFirstNameInitial("alice")).toBe("A");
  });

  it("trims whitespace", () => {
    expect(getFirstNameInitial("  Bob  ")).toBe("B");
  });

  it("returns fallback when empty", () => {
    expect(getFirstNameInitial("")).toBe("?");
    expect(getFirstNameInitial(null)).toBe("?");
    expect(getFirstNameInitial(undefined)).toBe("?");
  });
});
