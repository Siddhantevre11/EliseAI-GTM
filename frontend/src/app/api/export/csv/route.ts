import { NextRequest, NextResponse } from "next/server";

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { results } = body;

    const response = await fetch(`${PYTHON_BACKEND_URL}/export/csv`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ results }),
    });

    const data = await response.json();
    
    if (data.csv) {
      return new Response(data.csv, {
        status: 200,
        headers: {
          "Content-Type": "text/csv",
          "Content-Disposition": `attachment; filename="gtm_leads_${Date.now()}.csv"`,
        },
      });
    }
    
    return NextResponse.json(data);
  } catch (error) {
    console.error("CSV export error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}