const pptxgen = require("pptxgenjs");

// Palette: đô thị về đêm (navy) + đèn giao thông / vùng nóng bản đồ nhiệt (cam)
const NAVY = "0F1B3D";
const NAVY2 = "1C2B52";
const SLATE = "2D4263";
const AMBER = "F4A340";
const CORAL = "F4623A";
const ICE = "E9EEF9";
const WHITE = "FFFFFF";
const MUTED = "8B97B8";

function newDeck() {
  const p = new pptxgen();
  p.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  return p;
}

function darkBg(slide) {
  slide.background = { color: NAVY };
}
function lightBg(slide) {
  slide.background = { color: WHITE };
}

function title(slide, text, opts = {}) {
  slide.addText(text, {
    x: 0.6, y: 0.5, w: 12.1, h: opts.h || 0.9,
    fontFace: "Cambria", fontSize: opts.size || 30, bold: true,
    color: opts.color || NAVY, align: "left",
  });
}
function kicker(slide, text, color = AMBER) {
  slide.addText(text.toUpperCase(), {
    x: 0.6, y: 0.18, w: 10, h: 0.35,
    fontFace: "Calibri", fontSize: 12, bold: true, color, charSpacing: 2,
  });
}
function pageNum(slide, n, dark = false) {
  slide.addText(String(n), {
    x: 12.6, y: 7.05, w: 0.5, h: 0.3, fontFace: "Calibri", fontSize: 10,
    color: dark ? MUTED : "AAB2C8", align: "right",
  });
}

const pres = newDeck();

// ============================================================ SLIDE 1: TITLE
{
  const s = pres.addSlide(); darkBg(s);
  s.addShape("ellipse", { x: 9.6, y: -2.2, w: 7, h: 7, fill: { color: NAVY2 }, line: { type: "none" } });
  s.addShape("ellipse", { x: 11.2, y: -1.0, w: 3.6, h: 3.6, fill: { color: SLATE }, line: { type: "none" } });

  s.addText("BÀI TẬP LỚN — KHAI PHÁ DỮ LIỆU", {
    x: 0.9, y: 1.5, w: 8, h: 0.4, fontFace: "Calibri", fontSize: 13, bold: true,
    color: AMBER, charSpacing: 3,
  });
  s.addText("CityFlow", {
    x: 0.85, y: 1.95, w: 10, h: 1.3, fontFace: "Cambria", fontSize: 60, bold: true, color: WHITE,
  });
  s.addText(
    "Giám sát giao thông đô thị bằng truy vấn cửa sổ trượt\nvà khai phá mẫu đồng ùn tắc trên luồng dữ liệu quy mô lớn",
    { x: 0.9, y: 3.25, w: 9.5, h: 1.0, fontFace: "Calibri", fontSize: 18, color: ICE, lineSpacingMultiple: 1.25 }
  );

  s.addShape("line", { x: 0.9, y: 4.55, w: 3.2, h: 0, line: { color: AMBER, width: 2 } });

  s.addText(
    [
      { text: "Nhóm 15 — Lớp Hệ thống Thông tin 02, khóa 2025–2027\n", options: { bold: true, color: WHITE } },
      { text: "Nguyễn Thuý Anh · Trần Thị Thảo · Trần Văn Hanh\n", options: { color: ICE } },
      { text: "Giảng viên hướng dẫn: Thanh-Hà Đỗ", options: { color: MUTED, italic: true } },
    ],
    { x: 0.9, y: 4.85, w: 8, h: 1.3, fontFace: "Calibri", fontSize: 14, lineSpacingMultiple: 1.4 }
  );
  pageNum(s, 1, true);
}

// ==================================================== SLIDE 2: MOTIVATION
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Bối cảnh & động lực");
  title(s, "Bài toán: hàng trăm luồng đồng thời, bộ nhớ chỉ có giới hạn");

  s.addText(
    '"Có thể có nhiều luồng đồng thời — không thể giữ nhiều cửa sổ."',
    { x: 0.6, y: 1.55, w: 8.6, h: 0.9, fontFace: "Cambria", fontSize: 20, italic: true, color: SLATE, lineSpacingMultiple: 1.2 }
  );
  s.addText("— Slide chương Data Streaming, tr.53", {
    x: 0.6, y: 2.35, w: 6, h: 0.35, fontFace: "Calibri", fontSize: 12, color: MUTED,
  });

  const cards = [
    ["265", "khu vực taxi NYC,\nmỗi khu vực là một luồng"],
    ["535", "luồng song song\n(đón + trả + 5 vị từ)"],
    ["19,66M", "sự kiện chuyến đi\ntrong một tháng dữ liệu"],
  ];
  cards.forEach((c, i) => {
    const x = 0.6 + i * 4.15;
    s.addShape("roundRect", {
      x, y: 3.1, w: 3.85, h: 2.1, rectRadius: 0.12,
      fill: { color: ICE }, line: { type: "none" },
      shadow: { type: "outer", color: "1C2B52", opacity: 0.15, blur: 8, offset: 3, angle: 90 },
    });
    s.addText(c[0], { x, y: 3.35, w: 3.85, h: 0.9, align: "center", fontFace: "Cambria", fontSize: 40, bold: true, color: CORAL });
    s.addText(c[1], { x, y: 4.25, w: 3.85, h: 0.8, align: "center", fontFace: "Calibri", fontSize: 13, color: SLATE, lineSpacingMultiple: 1.15 });
  });

  s.addText(
    "Giữ cửa sổ đầy đủ N=10⁶ cho từng luồng × từng loại truy vấn ⇒ bộ nhớ tăng tuyến tính không kiểm soát được.",
    { x: 0.6, y: 5.55, w: 12.1, h: 0.6, fontFace: "Calibri", fontSize: 15, color: NAVY, italic: true }
  );
  pageNum(s, 2);
}

// ==================================================== SLIDE 3: SIX QUESTIONS
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Phát biểu bài toán");
  title(s, "Sáu câu hỏi nghiệp vụ — hai lớp bài toán");

  const rows = [
    ["Q1", "Bao nhiêu chuyến đón từ khu vực z trong N sự kiện gần nhất?", "DGIM"],
    ["Q2", "Tổng doanh thu của N chuyến gần nhất?", "DGIM số nguyên"],
    ["Q3", "Có bao nhiêu tuyến đường phân biệt đang hoạt động?", "Flajolet-Martin"],
    ["Q4", "Nhu cầu có đang tập trung bất thường không?", "AMS"],
    ["Q5", "Mẫu đại diện nào để phân tích sâu?", "Reservoir Sampling"],
    ["Q6", "Khu vực nào ùn tắc CÙNG NHAU?", "FP-Growth + độ đo"],
  ];
  let y = 1.65;
  rows.forEach((r, i) => {
    const bg = i === 5 ? { color: "FFF3E7" } : { color: i % 2 === 0 ? ICE : WHITE };
    s.addShape("roundRect", { x: 0.6, y, w: 12.1, h: 0.78, rectRadius: 0.06, fill: bg, line: { type: "none" } });
    s.addText(r[0], { x: 0.85, y, w: 0.7, h: 0.78, valign: "middle", fontFace: "Cambria", fontSize: 16, bold: true, color: i === 5 ? CORAL : SLATE });
    s.addText(r[1], { x: 1.6, y, w: 7.9, h: 0.78, valign: "middle", fontFace: "Calibri", fontSize: 13.5, color: NAVY });
    s.addText(r[2], { x: 9.6, y, w: 3.0, h: 0.78, valign: "middle", fontFace: "Calibri", fontSize: 12.5, bold: true, color: i === 5 ? CORAL : SLATE, align: "right" });
    y += 0.85;
  });
  s.addText("Lớp 1 (Q1–Q5): cửa sổ trượt xấp xỉ    ·    Lớp 2 (Q6): khai phá mẫu — thành phần BẮT BUỘC", {
    x: 0.6, y: 6.85, w: 12.1, h: 0.35, fontFace: "Calibri", fontSize: 12, italic: true, color: MUTED,
  });
  pageNum(s, 3);
}

// ==================================================== SLIDE 4: DATA
{
  const s = pres.addSlide(); darkBg(s);
  kicker(s, "Dữ liệu");
  s.addText("NYC TLC Trip Records — 19.663.928 sự kiện thật", {
    x: 0.6, y: 0.5, w: 12, h: 0.7, fontFace: "Cambria", fontSize: 26, bold: true, color: WHITE,
  });

  const stats = [
    ["0", "giá trị thiếu\ntrên 11 cột sử dụng"],
    ["265", "khu vực địa lý\nđịnh danh sẵn"],
    ["4,1×", "chênh lệch giờ cao/thấp điểm\n— xác nhận tính phi dừng"],
  ];
  stats.forEach((c, i) => {
    const x = 0.6 + i * 4.15;
    s.addShape("roundRect", { x, y: 1.5, w: 3.85, h: 1.9, rectRadius: 0.1, fill: { color: NAVY2 }, line: { type: "none" } });
    s.addText(c[0], { x, y: 1.65, w: 3.85, h: 0.85, align: "center", fontFace: "Cambria", fontSize: 34, bold: true, color: AMBER });
    s.addText(c[1], { x, y: 2.5, w: 3.85, h: 0.8, align: "center", fontFace: "Calibri", fontSize: 12.5, color: ICE, lineSpacingMultiple: 1.15 });
  });

  s.addText("Ba phát hiện làm thay đổi thiết kế:", {
    x: 0.6, y: 3.75, w: 8, h: 0.4, fontFace: "Calibri", fontSize: 15, bold: true, color: AMBER,
  });
  const findings = [
    "44,67% bản ghi lệch thứ tự thời gian → bắt buộc sắp xếp lại trước khi xử lý",
    "Phân phối doanh thu lệch phải mạnh → chốt m=8 bit thay vì giả định m=12",
    "Top-10 khu vực chỉ chiếm 13,3% → rời rạc hóa phải theo phân vị RIÊNG từng khu vực",
  ];
  let fy = 4.25;
  findings.forEach((f) => {
    s.addShape("ellipse", { x: 0.65, y: fy + 0.12, w: 0.1, h: 0.1, fill: { color: CORAL }, line: { type: "none" } });
    s.addText(f, { x: 0.95, y: fy, w: 11.3, h: 0.55, fontFace: "Calibri", fontSize: 14, color: ICE });
    fy += 0.65;
  });
  pageNum(s, 4, true);
}

// ==================================================== SLIDE 5: ARCHITECTURE
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Kiến trúc hệ thống");
  title(s, "Bảy tầng — từ luồng thô tới bảng điều khiển");

  const layers = [
    ["L0", "Ingestion & Replay", "Nạp + sắp xếp thời gian"],
    ["L1", "Streaming Sketch", "DGIM · FM · AMS · Reservoir"],
    ["L2", "State Store", "535 luồng, đồng hồ chung"],
    ["L3", "Mining Layer", "FP-Growth + 10 độ đo"],
    ["L4", "API Layer", "FastAPI"],
    ["L5", "Web Dashboard", "React + Leaflet"],
    ["L6", "Benchmark", "Đối chiếu oracle chính xác"],
  ];
  const w = 1.72, gap = 0.06, x0 = 0.6, y0 = 2.0;
  layers.forEach((l, i) => {
    const x = x0 + i * (w + gap);
    const isMining = l[0] === "L3";
    s.addShape("roundRect", {
      x, y: y0, w, h: 2.6, rectRadius: 0.08,
      fill: { color: isMining ? CORAL : SLATE }, line: { type: "none" },
    });
    s.addText(l[0], { x, y: y0 + 0.15, w, h: 0.4, align: "center", fontFace: "Cambria", fontSize: 15, bold: true, color: WHITE });
    s.addText(l[1], { x: x + 0.08, y: y0 + 0.6, w: w - 0.16, h: 0.9, align: "center", fontFace: "Calibri", fontSize: 11, bold: true, color: WHITE, lineSpacingMultiple: 1.1 });
    s.addText(l[2], { x: x + 0.06, y: y0 + 1.55, w: w - 0.12, h: 0.95, align: "center", fontFace: "Calibri", fontSize: 9.5, color: "E2E7F2", lineSpacingMultiple: 1.1 });
  });

  s.addText(
    "L3 (đỏ cam) là thành phần BẮT BUỘC: trả lời \"khu vực nào ùn tắc CÙNG NHAU\" — điều tầng sketch không làm được.",
    { x: 0.6, y: 4.95, w: 12.1, h: 0.5, fontFace: "Calibri", fontSize: 13.5, italic: true, color: NAVY }
  );
  s.addText(
    "Nguyên tắc thiết kế: (P1) một lượt, không quay lại  ·  (P2) bộ nhớ đo THẬT  ·  (P3) oracle tách biệt hoàn toàn  ·  (P4) from-scratch trước, thư viện chỉ để kiểm định  ·  (P5) mọi tham số cấu hình được",
    { x: 0.6, y: 5.7, w: 12.1, h: 1.1, fontFace: "Calibri", fontSize: 12.5, color: SLATE, lineSpacingMultiple: 1.3 }
  );
  pageNum(s, 5);
}

// ==================================================== SLIDE 6: DGIM THEORY
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Cơ sở lý thuyết");
  title(s, "DGIM — đếm bit 1 trong cửa sổ trượt");

  s.addText(
    [
      { text: "Ý tưởng: ", options: { bold: true, color: NAVY } },
      { text: "tóm tắt luồng bằng các bucket, kích thước LŨY THỪA 2 (1,1,2,4,8,…)\n\n", options: { color: SLATE } },
      { text: "Bốn bất biến:\n", options: { bold: true, color: NAVY } },
      { text: "1. Tối đa r bucket cùng kích thước\n", options: { color: SLATE, bullet: true } },
      { text: "2. Không chồng lấn timestamp\n", options: { color: SLATE, bullet: true } },
      { text: "3. Bucket mới nhỏ hơn bucket cũ hơn\n", options: { color: SLATE, bullet: true } },
      { text: "4. Loại bucket khi ra khỏi cửa sổ N", options: { color: SLATE, bullet: true } },
    ],
    { x: 0.6, y: 1.7, w: 5.6, h: 3.6, fontFace: "Calibri", fontSize: 14.5, lineSpacingMultiple: 1.3, paraSpaceAfter: 4 }
  );

  // minh họa bucket
  const buckets = [1, 1, 2, 4];
  let bx = 6.7;
  buckets.forEach((sz, i) => {
    const bw = 0.55 + Math.log2(sz) * 0.25;
    s.addShape("roundRect", {
      x: bx, y: 2.6, w: bw, h: 0.75, rectRadius: 0.05,
      fill: { color: i === buckets.length - 1 ? CORAL : SLATE }, line: { type: "none" },
    });
    s.addText(String(sz), { x: bx, y: 2.6, w: bw, h: 0.75, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 16, bold: true, color: WHITE });
    bx += bw + 0.15;
  });
  s.addText("Ước lượng = 1 + 1 + 2 + 4/2 = 6", {
    x: 6.7, y: 3.55, w: 5.5, h: 0.4, fontFace: "Calibri", fontSize: 13, italic: true, color: MUTED,
  });
  s.addText("(trừ nửa bucket CŨ NHẤT — không biết chính xác phần còn trong cửa sổ)", {
    x: 6.7, y: 3.95, w: 5.9, h: 0.5, fontFace: "Calibri", fontSize: 11, color: MUTED, italic: true,
  });

  s.addShape("roundRect", { x: 6.7, y: 4.7, w: 5.9, h: 2.0, rectRadius: 0.1, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("Định lý cận sai số", { x: 6.95, y: 4.85, w: 5.4, h: 0.4, fontFace: "Calibri", fontSize: 13, bold: true, color: AMBER });
  s.addText(
    "|ĉ − c| / c  ≤  (B/2) / B  =  50%\n\nvới B = kích thước bucket cũ nhất, r=2.\nTăng r → sai số giảm theo O(1/r).",
    { x: 6.95, y: 5.2, w: 5.4, h: 1.4, fontFace: "Cambria", fontSize: 14, color: WHITE, lineSpacingMultiple: 1.3 }
  );
  pageNum(s, 6);
}

// ==================================================== SLIDE 7: E1-E3 RESULTS
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Thực nghiệm E1–E3");
  title(s, "Ba cận lý thuyết — xác nhận trên 19,66 triệu sự kiện thật");

  s.addChart(pres.ChartType.line, [
    {
      name: "Sai số trung bình (%)",
      labels: ["r=2", "r=4", "r=8", "r=16"],
      values: [11.92, 5.18, 2.43, 1.29],
    },
  ], {
    x: 0.6, y: 1.55, w: 5.9, h: 3.1,
    showTitle: true, title: "E2 — Sai số DGIM theo r  (∝ O(1/r))", titleFontSize: 13, titleColor: NAVY,
    showValue: true, dataLabelPosition: "t", dataLabelFontSize: 10, dataLabelColor: SLATE,
    chartColors: [CORAL], lineSize: 3, lineDataSymbolSize: 7,
    catAxisLabelColor: SLATE, valAxisLabelColor: SLATE,
    valAxisTitle: "%", showValAxisTitle: true,
    valGridLine: { color: "E2E7F2", size: 1 }, catGridLine: { style: "none" },
    showLegend: false,
  });

  s.addChart(pres.ChartType.bar, [
    {
      name: "Bộ nhớ (byte)",
      labels: ["10⁴", "10⁵", "10⁶", "5×10⁶"],
      values: [8908, 9780, 11412, 13016],
    },
  ], {
    x: 6.85, y: 1.55, w: 5.9, h: 3.1,
    showTitle: true, title: "E3 — Bộ nhớ theo N (N tăng 500×, bộ nhớ chỉ 1,46×)", titleFontSize: 13, titleColor: NAVY,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelColor: SLATE,
    chartColors: [SLATE],
    catAxisLabelColor: SLATE, valAxisLabelColor: SLATE,
    valGridLine: { color: "E2E7F2", size: 1 }, catGridLine: { style: "none" },
    showLegend: false,
  });

  s.addShape("roundRect", { x: 0.6, y: 5.0, w: 12.1, h: 1.65, rectRadius: 0.1, fill: { color: ICE }, line: { type: "none" } });
  s.addText(
    [
      { text: "E1:  ", options: { bold: true, color: CORAL } },
      { text: "0 / 3.178 phép truy vấn vi phạm cận 50% — sai số max quan sát 46,3%\n", options: { color: NAVY } },
      { text: "E7:  ", options: { bold: true, color: CORAL } },
      { text: "87.933 sự kiện/giây (vượt mục tiêu 50.000) · 5,66 MB cho 535 luồng · tiết kiệm 11,8× so với lưu đầy đủ", options: { color: NAVY } },
    ],
    { x: 0.85, y: 5.2, w: 11.6, h: 1.3, fontFace: "Calibri", fontSize: 14, lineSpacingMultiple: 1.5 }
  );
  pageNum(s, 7);
}

// ==================================================== SLIDE 8: E4 HYPOTHESIS
{
  const s = pres.addSlide(); darkBg(s);
  kicker(s, "Đóng góp nghiên cứu độc lập");
  s.addText("Giả thuyết H1: phân bổ ngân sách DGIM mở rộng", {
    x: 0.6, y: 0.5, w: 12, h: 0.7, fontFace: "Cambria", fontSize: 25, bold: true, color: WHITE,
  });

  s.addText(
    "Tài liệu giảng dạy nêu công thức mở rộng DGIM cho tổng số nguyên nhưng KHÔNG bàn cách phân bổ ngân sách bộ nhớ giữa các luồng bit.",
    { x: 0.6, y: 1.4, w: 12, h: 0.6, fontFace: "Calibri", fontSize: 14.5, color: ICE, italic: true }
  );

  s.addShape("roundRect", { x: 0.6, y: 2.2, w: 5.7, h: 1.5, rectRadius: 0.1, fill: { color: NAVY2 }, line: { type: "none" } });
  s.addText("Suy dẫn bằng nhân tử Lagrange", { x: 0.85, y: 2.35, w: 5.2, h: 0.35, fontFace: "Calibri", fontSize: 13, bold: true, color: AMBER });
  s.addText("rᵢ  ∝  √( 2ⁱ · cᵢ )", { x: 0.85, y: 2.65, w: 5.2, h: 0.7, fontFace: "Cambria", fontSize: 26, bold: true, color: WHITE });
  s.addText("cân bằng trọng số 2ⁱ với tần suất thật cᵢ", { x: 0.85, y: 3.3, w: 5.2, h: 0.35, fontFace: "Calibri", fontSize: 11, italic: true, color: MUTED });

  s.addChart(pres.ChartType.bar, [
    {
      name: "Sai số trung bình (%)",
      labels: ["Đều", "Ưu tiên bit cao\n(trực giác)", "Công thức\nLagrange"],
      values: [2.119, 2.377, 1.615],
    },
  ], {
    x: 6.6, y: 2.1, w: 6.15, h: 3.3,
    showTitle: true, title: "Sai số ở ngân sách 32", titleColor: WHITE, titleFontSize: 13,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: WHITE,
    chartColors: [SLATE, CORAL, AMBER],
    catAxisLabelColor: ICE, valAxisLabelColor: ICE, catAxisLabelFontSize: 10,
    valGridLine: { color: "2D4263", size: 1 }, catGridLine: { style: "none" },
    showLegend: false, chartArea: { fill: { color: NAVY } }, plotArea: { fill: { color: NAVY } },
  });

  s.addShape("roundRect", { x: 0.6, y: 5.9, w: 12.1, h: 1.0, rectRadius: 0.1, fill: { color: "2B3A1E" }, line: { type: "none" } });
  s.addText(
    "Kết quả: công thức Lagrange tốt hơn phân bổ đều 23,8% — trực giác \"ưu tiên bit cao\" TỆ HƠN đều 12,2%. Bit gây sai số nhiều nhất là bit thứ 4, không phải bit cao nhất.",
    { x: 0.85, y: 6.05, w: 11.6, h: 0.7, fontFace: "Calibri", fontSize: 13, color: "D7F5C4", valign: "middle" }
  );
  pageNum(s, 8, true);
}

// ==================================================== SLIDE 9: E5-E6
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Thực nghiệm E5–E6");
  title(s, "Flajolet-Martin & AMS: chính xác chưa chắc đã đủ tín hiệu");

  s.addChart(pres.ChartType.line, [
    {
      name: "Sai số trung vị (%)",
      labels: ["8", "16", "32", "64", "128", "256"],
      values: [40.4, 26.0, 20.5, 14.2, 10.7, 6.4],
    },
  ], {
    x: 0.6, y: 1.55, w: 5.9, h: 3.2,
    showTitle: true, title: "FM: sai số giảm theo m (vượt cận 11,2% tại m≥128)", titleFontSize: 12.5, titleColor: NAVY,
    showValue: true, dataLabelPosition: "t", dataLabelFontSize: 9, dataLabelColor: SLATE,
    chartColors: [CORAL], lineSize: 3, lineDataSymbolSize: 6,
    catAxisLabelColor: SLATE, valAxisLabelColor: SLATE,
    valAxisTitle: "%", showValAxisTitle: true,
    valGridLine: { color: "E2E7F2", size: 1 }, catGridLine: { style: "none" },
    showLegend: false,
  });

  s.addShape("roundRect", { x: 6.85, y: 1.55, w: 5.9, h: 3.2, rectRadius: 0.1, fill: { color: ICE }, line: { type: "none" } });
  s.addText("AMS — tín hiệu số bất ngờ", { x: 7.1, y: 1.75, w: 5.4, h: 0.4, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY });
  s.addText(
    [
      { text: "Sai số ước lượng (k=100):  ", options: { color: SLATE } }, { text: "7,1%  ✓\n\n", options: { bold: true, color: "1A7A3C" } },
      { text: "Nhưng tỷ lệ bất thường/trung vị:\n", options: { color: SLATE } },
      { text: "  5,0×  ", options: { color: MUTED, strike: true } }, { text: " thô  →  ", options: { color: SLATE } },
      { text: "2,7×", options: { bold: true, color: CORAL } }, { text: "  sau chuẩn hóa n²\n\n", options: { color: SLATE } },
      { text: "⇒ Phân phối NYC khá đều — cần tầng khai phá mẫu (Q6) để trả lời \"ở đâu, cùng ai\".", options: { italic: true, color: NAVY } },
    ],
    { x: 7.1, y: 2.2, w: 5.4, h: 2.4, fontFace: "Calibri", fontSize: 13, lineSpacingMultiple: 1.3 }
  );

  s.addText(
    "Phát hiện: hằng số hiệu chỉnh kinh điển φ=0,77351 KHÔNG áp dụng được cho sơ đồ này — dành cho một biến thể FM khác — áp dụng nhầm làm sai số TĂNG thay vì giảm.",
    { x: 0.6, y: 5.0, w: 12.1, h: 0.9, fontFace: "Calibri", fontSize: 13, italic: true, color: SLATE }
  );
  pageNum(s, 9);
}

// ==================================================== SLIDE 10: E7 STORY
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Thực nghiệm E7");
  title(s, "Nút thắt hiệu năng không nằm ở nơi dự đoán");

  s.addShape("roundRect", { x: 0.6, y: 1.6, w: 5.85, h: 3.6, rectRadius: 0.1, fill: { color: "FBEAEA" }, line: { type: "none" } });
  s.addText("TRƯỚC", { x: 0.85, y: 1.8, w: 5, h: 0.4, fontFace: "Calibri", fontSize: 13, bold: true, color: "B02A2A" });
  s.addText("7.077", { x: 0.85, y: 2.15, w: 5.3, h: 0.9, fontFace: "Cambria", fontSize: 42, bold: true, color: "B02A2A" });
  s.addText("sự kiện / giây", { x: 0.85, y: 2.95, w: 5, h: 0.4, fontFace: "Calibri", fontSize: 13, color: "8B3A3A" });
  s.addText(
    "535 luồng DGIM: chỉ 1,5% thời gian\nFlajolet-Martin (m=256): 97,2% thời gian\n\n→ tối ưu độ chính xác (E5) đã âm thầm phá vỡ hiệu năng hệ thống",
    { x: 0.85, y: 3.55, w: 5.3, h: 1.5, fontFace: "Calibri", fontSize: 12.5, color: "5C2626", lineSpacingMultiple: 1.35 }
  );

  s.addShape("roundRect", { x: 6.85, y: 1.6, w: 5.85, h: 3.6, rectRadius: 0.1, fill: { color: "E8F5E9" }, line: { type: "none" } });
  s.addText("SAU — VECTOR HÓA", { x: 7.1, y: 1.8, w: 5, h: 0.4, fontFace: "Calibri", fontSize: 13, bold: true, color: "1A7A3C" });
  s.addText("87.933", { x: 7.1, y: 2.15, w: 5.3, h: 0.9, fontFace: "Cambria", fontSize: 42, bold: true, color: "1A7A3C" });
  s.addText("sự kiện / giây  (×12,4)", { x: 7.1, y: 2.95, w: 5, h: 0.4, fontFace: "Calibri", fontSize: 13, color: "2E7D4F" });
  s.addText(
    "Gom cả lô vào MỘT phép toán numpy cho toàn bộ m hàm băm — tận dụng tính KẾT HỢP và LŨY ĐẲNG của phép max\n\nKiểm chứng: R khớp TUYỆT ĐỐI với đường xử lý từng phần tử",
    { x: 7.1, y: 3.55, w: 5.3, h: 1.5, fontFace: "Calibri", fontSize: 12.5, color: "1E5631", lineSpacingMultiple: 1.35 }
  );

  s.addText("Bài học: đo trước khi tối ưu — tối ưu cục bộ một thành phần có thể phá vỡ hiệu năng toàn hệ thống.", {
    x: 0.6, y: 5.5, w: 12.1, h: 0.5, fontFace: "Calibri", fontSize: 14, italic: true, color: NAVY,
  });
  pageNum(s, 10);
}

// ==================================================== SLIDE 11: NULL-INVARIANCE — HERO SLIDE
{
  const s = pres.addSlide(); darkBg(s);
  kicker(s, "⭐ Kết quả nổi bật nhất — E10");
  s.addText("Bằng chứng hoàn hảo cho tính bất biến với giao dịch rỗng", {
    x: 0.6, y: 0.5, w: 12, h: 0.8, fontFace: "Cambria", fontSize: 26, bold: true, color: WHITE,
  });

  s.addText(
    "Luật thật: Midtown Center ⇒ Midtown East — thêm dần giao dịch rỗng (tối đa gấp 100 lần dữ liệu gốc)",
    { x: 0.6, y: 1.35, w: 12, h: 0.4, fontFace: "Calibri", fontSize: 13, italic: true, color: MUTED }
  );

  s.addChart(pres.ChartType.bar, [
    {
      name: "Biến thiên (%)",
      labels: ["6 độ đo\nbất biến", "Lift", "Chi-bình\nphương"],
      values: [0.0, 10000, 10259],
    },
  ], {
    x: 1.5, y: 1.9, w: 10.3, h: 4.3,
    showTitle: true, title: "Biến thiên khi thêm giao dịch rỗng gấp 100 lần", titleColor: WHITE, titleFontSize: 14,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 13, dataLabelColor: WHITE, dataLabelFormatCode: "#,##0\"%\"",
    chartColors: ["4CAF7D", CORAL, "C0392B"],
    catAxisLabelColor: ICE, valAxisLabelColor: ICE, catAxisLabelFontSize: 13,
    valGridLine: { color: "2D4263", size: 1 }, catGridLine: { style: "none" },
    showLegend: false, chartArea: { fill: { color: NAVY } }, plotArea: { fill: { color: NAVY } },
  });

  s.addText(
    "Confidence, All-Confidence, Coherence, Cosine, Kulczynski, Max-Confidence, Imbalance Ratio  —  không dùng n  ⇒  không thể bị ảnh hưởng",
    { x: 0.6, y: 6.55, w: 12.1, h: 0.5, fontFace: "Calibri", fontSize: 12.5, italic: true, color: AMBER, align: "center" }
  );
  pageNum(s, 11, true);
}

// ==================================================== SLIDE 12: REAL PATTERNS FOUND
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Kết quả E9–E11");
  title(s, "Luật đồng ùn tắc mang ý nghĩa địa lý thật");

  const rules = [
    ["Midtown Center ⇒ Midtown East", "0,897", "9,03", "hai khu vực liền kề trung tâm Manhattan"],
    ["East Village+Williamsburg(N) ⇒ Bushwick S+Williamsburg(S)", "0,892", "11,27", "cụm giải trí đêm Brooklyn"],
    ["Bushwick N+Greenwich Village S ⇒ East Village+Lower East Side", "0,885", "10,92", "cụm liền kề Đông Manhattan"],
  ];
  s.addShape("roundRect", { x: 0.6, y: 1.55, w: 12.1, h: 0.5, rectRadius: 0.05, fill: { color: NAVY }, line: { type: "none" } });
  ["Luật", "Kulczynski", "Lift", "Diễn giải"].forEach((h, i) => {
    const xs = [0.75, 7.0, 8.5, 9.7];
    const ws = [6.2, 1.4, 1.1, 2.85];
    s.addText(h, { x: xs[i], y: 1.55, w: ws[i], h: 0.5, valign: "middle", fontFace: "Calibri", fontSize: 12, bold: true, color: WHITE });
  });
  let ry = 2.1;
  rules.forEach((r, i) => {
    s.addShape("roundRect", { x: 0.6, y: ry, w: 12.1, h: 1.05, rectRadius: 0.05, fill: { color: i % 2 === 0 ? ICE : WHITE }, line: { type: "none" } });
    s.addText(r[0], { x: 0.75, y: ry, w: 6.2, h: 1.05, valign: "middle", fontFace: "Calibri", fontSize: 11.5, color: NAVY });
    s.addText(r[1], { x: 7.0, y: ry, w: 1.4, h: 1.05, valign: "middle", fontFace: "Cambria", fontSize: 14, bold: true, color: CORAL });
    s.addText(r[2], { x: 8.5, y: ry, w: 1.1, h: 1.05, valign: "middle", fontFace: "Cambria", fontSize: 14, bold: true, color: SLATE });
    s.addText(r[3], { x: 9.7, y: ry, w: 2.85, h: 1.05, valign: "middle", fontFace: "Calibri", fontSize: 11, italic: true, color: MUTED });
    ry += 1.12;
  });

  s.addText(
    "484 luật từ 355 mẫu thường xuyên (min_sup=7%) · Imbalance Ratio thấp (≈0,003–0,13) ⇒ hai khu vực bận rộn CÂN BẰNG, không bên nào lấn át",
    { x: 0.6, y: 5.55, w: 12.1, h: 0.5, fontFace: "Calibri", fontSize: 12.5, italic: true, color: SLATE }
  );
  pageNum(s, 12);
}

// ==================================================== SLIDE 13: FP-GROWTH vs APRIORI
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Thực nghiệm E9");
  title(s, "FP-Growth vs Apriori: 3 điểm nghẽn định lượng trên dữ liệu thật");

  s.addChart(pres.ChartType.bar, [
    { name: "FP-Growth (s)", labels: ["10%", "7%", "5%"], values: [0.018, 0.868, 6.28] },
    { name: "Apriori (s)", labels: ["10%", "7%", "5%"], values: [0.157, 78.99, 213.3] },
  ], {
    x: 0.6, y: 1.6, w: 6.1, h: 3.5,
    showTitle: true, title: "Thời gian chạy theo ngưỡng hỗ trợ (giây, thang log)", titleFontSize: 12.5, titleColor: NAVY,
    barGapWidthPct: 40,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 9, dataLabelColor: SLATE,
    chartColors: [CORAL, SLATE],
    catAxisLabelColor: SLATE, valAxisLabelColor: SLATE,
    valAxisMinVal: 0.001, valAxisMaxVal: 1000,
    valGridLine: { color: "E2E7F2", size: 1 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendColor: SLATE, legendFontSize: 11,
  });

  s.addShape("roundRect", { x: 7.0, y: 1.6, w: 5.7, h: 3.5, rectRadius: 0.1, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("Tại min_sup = 5%", { x: 7.25, y: 1.8, w: 5.2, h: 0.4, fontFace: "Calibri", fontSize: 13, bold: true, color: AMBER });
  const items = [
    ["91,0×", "tăng tốc đỉnh (tại 7%)"],
    ["61.329", "ứng viên cho 16.319 mẫu thật"],
    ["181.750.272", "phép kiểm tra hỗ trợ"],
    ["73,6%", "còn lại sau nén bằng mẫu đóng — KHÔNG mất thông tin"],
  ];
  let iy = 2.3;
  items.forEach((it) => {
    s.addText(it[0], { x: 7.25, y: iy, w: 2.1, h: 0.55, fontFace: "Cambria", fontSize: 19, bold: true, color: WHITE });
    s.addText(it[1], { x: 9.35, y: iy, w: 3.15, h: 0.55, valign: "middle", fontFace: "Calibri", fontSize: 10.5, color: ICE });
    iy += 0.68;
  });

  s.addText(
    "Hai thuật toán độc lập cho kết quả GIỐNG HỆT NHAU ở mọi ngưỡng — kiểm chứng tính đúng đắn trực tiếp trong mã nguồn thực nghiệm.",
    { x: 0.6, y: 5.35, w: 12.1, h: 0.6, fontFace: "Calibri", fontSize: 13, italic: true, color: SLATE }
  );
  pageNum(s, 13);
}

// ==================================================== SLIDE 14: VERIFICATION
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Kiểm chứng tính đúng đắn");
  title(s, "158 kiểm định · sai lệch với thư viện tham chiếu = 0");

  const cols = [
    ["158/158", "kiểm định đơn vị đạt", "tái hiện trực tiếp ví dụ số trong tài liệu giảng dạy"],
    ["20/20", "phép đối chiếu mlxtend", "FP-Growth from-scratch khớp TUYỆT ĐỐI thư viện tham chiếu"],
    ["3", "đường độc lập cho cùng kết quả", "FP-Growth · Apriori · mlxtend — cùng tập mục, cùng số đếm"],
  ];
  cols.forEach((c, i) => {
    const x = 0.6 + i * 4.15;
    s.addShape("roundRect", { x, y: 1.7, w: 3.85, h: 2.6, rectRadius: 0.1, fill: { color: ICE }, line: { type: "none" } });
    s.addText(c[0], { x, y: 1.9, w: 3.85, h: 0.85, align: "center", fontFace: "Cambria", fontSize: 32, bold: true, color: CORAL });
    s.addText(c[1], { x: x + 0.2, y: 2.75, w: 3.45, h: 0.5, align: "center", fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY });
    s.addText(c[2], { x: x + 0.25, y: 3.3, w: 3.35, h: 0.9, align: "center", fontFace: "Calibri", fontSize: 10.5, color: SLATE, lineSpacingMultiple: 1.2 });
  });

  s.addText("Ví dụ ví dụ số tái hiện làm kiểm định:", {
    x: 0.6, y: 4.65, w: 8, h: 0.4, fontFace: "Calibri", fontSize: 14, bold: true, color: NAVY,
  });
  const examples = [
    "DGIM: bucket {1,1,2,4} → ước lượng = 6  (slide tr.65)",
    "AMS: luồng 15 phần tử → ước lượng = 55  (slide tr.48)",
    "FP-Growth: f-list {f,c,a,b,m,p}, min_sup=3  (slide tr.22)",
  ];
  let ey = 5.15;
  examples.forEach((e) => {
    s.addText("✓  " + e, { x: 0.8, y: ey, w: 11.5, h: 0.4, fontFace: "Calibri", fontSize: 12.5, color: SLATE });
    ey += 0.42;
  });
  pageNum(s, 14);
}

// ==================================================== SLIDE 15: PRODUCT
{
  const s = pres.addSlide(); darkBg(s);
  kicker(s, "Sản phẩm hoàn chỉnh");
  s.addText("Từ thuật toán tới hệ thống hoạt động", {
    x: 0.6, y: 0.5, w: 12, h: 0.7, fontFace: "Cambria", fontSize: 27, bold: true, color: WHITE,
  });

  const parts = [
    ["API", "FastAPI — mỗi endpoint trả kèm cận lý thuyết & tham số"],
    ["CSDL", "PostgreSQL — 7 bảng, đã kiểm chứng ghi/đọc dữ liệu thật"],
    ["Dashboard", "React + Leaflet + Recharts — 4 màn hình trực quan"],
    ["Docker", "docker-compose — triển khai 3 dịch vụ một lệnh"],
  ];
  parts.forEach((p, i) => {
    const x = 0.6 + i * 3.1;
    s.addShape("roundRect", { x, y: 1.8, w: 2.85, h: 3.0, rectRadius: 0.1, fill: { color: NAVY2 }, line: { type: "none" } });
    s.addShape("roundRect", { x: x + 0.35, y: 2.1, w: 2.15, h: 0.55, rectRadius: 0.28, fill: { color: CORAL }, line: { type: "none" } });
    s.addText(p[0], { x: x + 0.35, y: 2.1, w: 2.15, h: 0.55, align: "center", valign: "middle", fontFace: "Calibri", fontSize: 13, bold: true, color: WHITE });
    s.addText(p[1], { x: x + 0.2, y: 2.85, w: 2.45, h: 1.75, fontFace: "Calibri", fontSize: 11, color: ICE, lineSpacingMultiple: 1.3 });
  });

  s.addText(
    "Live Monitor (bản đồ nhiệt)  ·  Accuracy Lab  ·  Pattern Explorer (đảo thứ hạng luật)  ·  Benchmark Dashboard",
    { x: 0.6, y: 5.1, w: 12.1, h: 0.5, fontFace: "Calibri", fontSize: 13.5, italic: true, color: MUTED, align: "center" }
  );
  pageNum(s, 15, true);
}

// ==================================================== SLIDE 16: CONCLUSION
{
  const s = pres.addSlide(); lightBg(s);
  kicker(s, "Kết luận");
  title(s, "Ba đóng góp chính");

  const contribs = [
    ["1", "Xác nhận đầy đủ", "cận sai số 50%, quan hệ O(1/r), bộ nhớ O(log²N) của DGIM trên dữ liệu thật quy mô lớn"],
    ["2", "Giả thuyết nghiên cứu độc lập", "phân bổ ngân sách DGIM mở rộng — suy dẫn Lagrange, xác nhận lý thuyết, bác bỏ trực giác"],
    ["3", "Bằng chứng null-invariance hoàn hảo", "biến thiên 0,0% so với 10.259% của χ² — số liệu thay lời phê phán lý thuyết"],
  ];
  let cy = 1.7;
  contribs.forEach((c) => {
    s.addShape("ellipse", { x: 0.6, y: cy, w: 0.75, h: 0.75, fill: { color: CORAL }, line: { type: "none" } });
    s.addText(c[0], { x: 0.6, y: cy, w: 0.75, h: 0.75, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 24, bold: true, color: WHITE });
    s.addText(c[1], { x: 1.6, y: cy - 0.05, w: 11, h: 0.45, fontFace: "Calibri", fontSize: 16, bold: true, color: NAVY });
    s.addText(c[2], { x: 1.6, y: cy + 0.4, w: 11, h: 0.55, fontFace: "Calibri", fontSize: 13, color: SLATE, lineSpacingMultiple: 1.2 });
    cy += 1.25;
  });

  s.addShape("roundRect", { x: 0.6, y: 5.55, w: 12.1, h: 1.1, rectRadius: 0.1, fill: { color: ICE }, line: { type: "none" } });
  s.addText(
    "Hướng phát triển: mở rộng 12 tháng dữ liệu · kết nối luồng thời gian thực · phát hiện trôi khái niệm · kết hợp đặc trưng ngữ cảnh (thời tiết, sự kiện)",
    { x: 0.85, y: 5.7, w: 11.6, h: 0.85, valign: "middle", fontFace: "Calibri", fontSize: 13, italic: true, color: NAVY }
  );
  pageNum(s, 16);
}

// ==================================================== SLIDE 17: THANK YOU
{
  const s = pres.addSlide(); darkBg(s);
  s.addShape("ellipse", { x: -2.5, y: 4.5, w: 6, h: 6, fill: { color: NAVY2 }, line: { type: "none" } });
  s.addText("Cảm ơn quý thầy/cô", {
    x: 0.9, y: 2.6, w: 11, h: 1.1, fontFace: "Cambria", fontSize: 48, bold: true, color: WHITE,
  });
  s.addText("Câu hỏi & thảo luận", {
    x: 0.9, y: 3.6, w: 8, h: 0.6, fontFace: "Calibri", fontSize: 20, color: AMBER,
  });
  s.addText("CityFlow — Nhóm 15 — Hệ thống Thông tin 02, khóa 2025–2027", {
    x: 0.9, y: 6.6, w: 10, h: 0.4, fontFace: "Calibri", fontSize: 12, color: MUTED,
  });
}

pres.writeFile({ fileName: "CityFlow_Slide_Bao_Ve.pptx" }).then(() => {
  console.log("Da tao file CityFlow_Slide_Bao_Ve.pptx");
});
