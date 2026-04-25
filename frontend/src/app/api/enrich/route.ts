import { NextRequest, NextResponse } from "next/server";

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const lead = await request.json();

    const response = await fetch(`${PYTHON_BACKEND_URL}/enrich`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lead),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Backend error", details: await response.text() },
        { status: 500 }
      );
    }

    const result = await response.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error("API route error:", error);
    return NextResponse.json(
      {
        tier: null,
        score_rationale: "Backend not available. Start with: python main.py",
        email_draft: { subject: "", body: "" },
        talking_points: [],
        key_data_points: {},
        buying_signals: {},
        objection_handling: {},
        sales_signal: "",
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 200 }
    );
  }
}