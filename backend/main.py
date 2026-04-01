"""
Internal Shelving Quoting Tool — Backend (Prototype)

Simplified quoting engine: takes shelving parameters and returns
a bill of materials with generated SKUs, quantities, and pricing.

Component logic:
- Upright frames are spaced 1 m apart → (length + 1) frames
- Shelves sit between frames, stacked every 1 m vertically
  (floor level up to height − 1 m, none at the very top)
- End caps: 2 per upright frame (top + bottom)
- Back panels: one 1×1 m panel behind each shelf
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Shelving Quoting Tool", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pricing tables
# ---------------------------------------------------------------------------

# Upright frames: price depends on height × depth
FRAME_PRICE: dict[tuple[int, float], float] = {
    (1, 0.5): 42.00,
    (1, 1.0): 56.00,
    (2, 0.5): 74.00,
    (2, 1.0): 95.00,
    (3, 0.5): 108.00,
    (3, 1.0): 137.00,
}

# Shelves (1 m wide): price depends on depth
SHELF_PRICE: dict[float, float] = {
    0.5: 24.00,
    1.0: 38.00,
}

# Back panels are always 1×1 m
BACK_PANEL_PRICE = 15.00

# End caps (top/bottom of each upright)
END_CAP_PRICE = 3.50

# White surcharge per component type
COLOR_SURCHARGE: dict[str, dict[str, float]] = {
    "Black": {"frame": 0.0, "shelf": 0.0, "back_panel": 0.0, "end_cap": 0.0},
    "White": {"frame": 8.0, "shelf": 4.0, "back_panel": 2.0, "end_cap": 0.50},
}

COLOR_ABBREV = {"Black": "BLK", "White": "WHT"}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class QuoteRequest(BaseModel):
    total_length: int = Field(..., gt=0, description="Total shelving length in whole meters")
    height: int = Field(..., ge=1, le=3, description="Frame height in meters (1, 2, or 3)")
    depth: float = Field(..., description="Shelf depth in meters (0.5 or 1.0)")
    frame_color: str = Field(..., description="Frame color: Black or White")
    add_back_panel: bool = False
    add_end_caps: bool = False


class LineItem(BaseModel):
    sku: str
    component: str
    quantity: int
    unit_price: float
    line_total: float


class QuoteResponse(BaseModel):
    input_summary: dict
    sections: int
    line_items: list[LineItem]
    subtotal: float
    total: float


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cm(meters: float) -> int:
    return int(meters * 100)


def _line(sku: str, component: str, qty: int, unit_price: float) -> LineItem:
    return LineItem(
        sku=sku,
        component=component,
        quantity=qty,
        unit_price=round(unit_price, 2),
        line_total=round(qty * unit_price, 2),
    )


def compute_quote(req: QuoteRequest) -> QuoteResponse:
    sections = req.total_length  # 1 m per section
    uprights = sections + 1
    shelf_levels = req.height  # one at floor, then every 1 m, none at the top
    total_shelves = shelf_levels * sections

    clr = COLOR_ABBREV[req.frame_color]
    surcharge = COLOR_SURCHARGE[req.frame_color]
    h_cm = _cm(req.height)
    d_cm = _cm(req.depth)

    items: list[LineItem] = []

    # --- Upright frames ---
    frame_price = FRAME_PRICE[(req.height, req.depth)] + surcharge["frame"]
    items.append(_line(
        sku=f"FRAME-{h_cm}H-{d_cm}D-{clr}",
        component=f"Upright Frame ({req.height * 100:.0f} × {req.depth * 100:.0f} cm, {req.frame_color})",
        qty=uprights,
        unit_price=frame_price,
    ))

    # --- Shelves ---
    shelf_price = SHELF_PRICE[req.depth] + surcharge["shelf"]
    items.append(_line(
        sku=f"SHELF-100W-{d_cm}D-{clr}",
        component=f"Shelf Board (100 × {req.depth * 100:.0f} cm, {req.frame_color})",
        qty=total_shelves,
        unit_price=shelf_price,
    ))

    # --- Back panels (optional) — one 1×1 m panel per shelf ---
    if req.add_back_panel:
        bp_price = BACK_PANEL_PRICE + surcharge["back_panel"]
        items.append(_line(
            sku=f"BACK-100x100-{clr}",
            component=f"Back Panel (100 × 100 cm, {req.frame_color})",
            qty=total_shelves,
            unit_price=bp_price,
        ))

    # --- End caps (optional) — 2 per upright frame ---
    if req.add_end_caps:
        cap_price = END_CAP_PRICE + surcharge["end_cap"]
        items.append(_line(
            sku=f"ENDCAP-{clr}",
            component=f"End Cap ({req.frame_color})",
            qty=uprights * 2,
            unit_price=cap_price,
        ))

    subtotal = round(sum(i.line_total for i in items), 2)

    return QuoteResponse(
        input_summary={
            "total_length": req.total_length,
            "height": req.height,
            "depth": req.depth,
            "frame_color": req.frame_color,
            "add_back_panel": req.add_back_panel,
            "add_end_caps": req.add_end_caps,
        },
        sections=sections,
        line_items=items,
        subtotal=subtotal,
        total=subtotal,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}


@app.post("/generate-quote", response_model=QuoteResponse)
def generate_quote(req: QuoteRequest):
    return compute_quote(req)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
