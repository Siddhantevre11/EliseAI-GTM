import { NextRequest, NextResponse } from "next/server";
import { PYTHON_BACKEND_URL } from "@/lib/backendConfig";

export async function POST(request: NextRequest) {
  const endpoint = "slack";
  console.log(`Proxying request to: ${PYTHON_BACKEND_URL}/${endpoint}`);

  try {
    const body = await request.json();
    const { lead, result } = body;

    const response = await fetch(`${PYTHON_BACKEND_URL}/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lead, result }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error [${endpoint}]:`, errorText);
      return NextResponse.json(
        { success: false, error: "Service temporarily unavailable. Please try again." },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Proxy error [${endpoint}]:`, error);
    return NextResponse.json(
      { success: false, error: "Service temporarily unavailable. Please try again." },
      { status: 502 }
    );
  }
}