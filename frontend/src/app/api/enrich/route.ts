import { NextRequest, NextResponse } from "next/server";
import { PYTHON_BACKEND_URL } from "@/lib/backendConfig";

export async function POST(request: NextRequest) {
  const endpoint = "enrich";
  console.log(`Proxying request to: ${PYTHON_BACKEND_URL}/${endpoint}`);

  try {
    const lead = await request.json();

    const response = await fetch(`${PYTHON_BACKEND_URL}/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lead),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error [${endpoint}]:`, errorText);
      return NextResponse.json(
        { error: "Service temporarily unavailable. Please try again." },
        { status: 502 }
      );
    }

    const result = await response.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error(`Proxy error [${endpoint}]:`, error);
    return NextResponse.json(
      { error: "Service temporarily unavailable. Please try again." },
      { status: 502 }
    );
  }
}