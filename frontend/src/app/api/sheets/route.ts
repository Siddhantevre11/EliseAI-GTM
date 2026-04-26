import { NextRequest, NextResponse } from "next/server";

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { lead, result } = body;

    const response = await fetch(`${PYTHON_BACKEND_URL}/sheets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lead, result }),
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Sheets API error:", error);
    return NextResponse.json(
      { success: false, error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}