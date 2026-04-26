import { NextRequest, NextResponse } from "next/server";
import { PYTHON_BACKEND_URL } from "@/lib/backendConfig";

export async function POST(request: NextRequest) {
  const endpoint = "export/csv";
  console.log(`Proxying request to: ${PYTHON_BACKEND_URL}/${endpoint}`);

  try {
    const body = await request.json();
    const { results } = body;

    const response = await fetch(`${PYTHON_BACKEND_URL}/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ results }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error [${endpoint}]:`, errorText);
      return NextResponse.json(
        { error: "Service temporarily unavailable. Please try again." },
        { status: 502 }
      );
    }

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
    console.error(`Proxy error [${endpoint}]:`, error);
    return NextResponse.json(
      { error: "Service temporarily unavailable. Please try again." },
      { status: 502 }
    );
  }
}