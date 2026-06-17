const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  VerticalAlign, LevelFormat, PageBreak
} = require('docx');
const fs = require('fs');

// ─── COLORS & DIMENSIONS ─────────────────────────────────────────────────────
const NAVY    = "1F3864";
const BLUE    = "2E75B6";
const LBL_BG  = "D6E4F0";  // label cell background
const HDR_BG  = "1F497D";  // title row background
const WHITE   = "FFFFFF";

const TW  = 9200;   // total table width (DXA)
const C1  = 2500;   // label column
const C2  = 6700;   // content column

// ─── BORDERS ─────────────────────────────────────────────────────────────────
const bd = { style: BorderStyle.SINGLE, size: 4, color: "ADB9CA" };
const B  = { top: bd, bottom: bd, left: bd, right: bd };

// ─── HELPERS ─────────────────────────────────────────────────────────────────
const run = (text, opts = {}) =>
  new TextRun({ text, font: "Times New Roman", size: 22, ...opts });

const para = (text, opts = {}) =>
  new Paragraph({ children: [run(text, opts)], ...opts });

const stepPara = (text, n) =>
  new Paragraph({
    indent: { left: 360, hanging: 260 },
    spacing: { after: 60 },
    children: [run(`${n}. ${text}`)]
  });

const bulletPara = (text) =>
  new Paragraph({
    indent: { left: 360, hanging: 260 },
    spacing: { after: 60 },
    children: [run('\u2022  ' + text)]
  });

const altPara = (text) =>
  new Paragraph({
    indent: { left: 360, hanging: 260 },
    spacing: { after: 60 },
    children: [run(text, { italics: true })]
  });

function lbl(text) {
  return new TableCell({
    borders: B,
    width: { size: C1, type: WidthType.DXA },
    shading: { fill: LBL_BG, type: ShadingType.CLEAR },
    margins: { top: 100, bottom: 100, left: 140, right: 80 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ children: [run(text, { bold: true })] })]
  });
}

function val(children) {
  if (!Array.isArray(children)) children = [para(children)];
  return new TableCell({
    borders: B,
    width: { size: C2, type: WidthType.DXA },
    shading: { fill: WHITE, type: ShadingType.CLEAR },
    margins: { top: 100, bottom: 100, left: 140, right: 100 },
    children
  });
}

function titleRow(name, code) {
  return new TableRow({
    children: [new TableCell({
      columnSpan: 2,
      borders: B,
      width: { size: TW, type: WidthType.DXA },
      shading: { fill: HDR_BG, type: ShadingType.CLEAR },
      margins: { top: 140, bottom: 140, left: 160, right: 160 },
      children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          run(name, { bold: true, size: 24, color: WHITE }),
          run(`   [${code}]`, { size: 20, color: "BDD7EE" })
        ]
      })]
    })]
  });
}

function row(labelText, children) {
  return new TableRow({ children: [lbl(labelText), val(children)] });
}

function ucTable(uc) {
  return new Table({
    width: { size: TW, type: WidthType.DXA },
    columnWidths: [C1, C2],
    rows: [
      titleRow(uc.name, uc.code),
      row("Mã chức năng",          [para(uc.code)]),
      row("Tác nhân",              [para(uc.actors)]),
      row("Mục tiêu",              [para(uc.goal)]),
      row("Tiền điều kiện",        uc.pre.map(bulletPara)),
      row("Luồng sự kiện chính",   uc.main.map((t, i) => stepPara(t, i + 1))),
      row("Luồng rẽ nhánh",        uc.alt.map(altPara)),
      row("Hậu điều kiện",         uc.post.map(bulletPara)),
    ]
  });
}

const gap = () => new Paragraph({ spacing: { after: 240 }, children: [run("")] });

// ─── DATA ─────────────────────────────────────────────────────────────────────
const SECTIONS = [
  {
    heading: "2.3.1. Quản Lý Hồ Sơ Khách Hàng",
    ucs: [
      {
        name: "Mở Hồ Sơ Khách Hàng",
        code: "UC-CS-01",
        actors: "Giao dịch viên",
        goal: "Tạo hồ sơ mới cho khách hàng chưa có trong hệ thống ngân hàng.",
        pre: [
          "Giao dịch viên đã đăng nhập vào hệ thống.",
          "Khách hàng đủ 18 tuổi trở lên.",
          "CCCD của khách hàng chưa được đăng ký trong hệ thống."
        ],
        main: [
          'Giao dịch viên chọn chức năng "Mở Hồ Sơ Khách Hàng".',
          "Hệ thống hiển thị form nhập thông tin khách hàng.",
          "Giao dịch viên nhập thông tin: họ tên, CCCD, ngày sinh, quốc tịch, địa chỉ, chi nhánh đăng ký.",
          "Giao dịch viên xác nhận thông tin đã nhập.",
          "Hệ thống kiểm tra tính hợp lệ: CCCD, độ tuổi, trùng lặp dữ liệu.",
          "Hệ thống tạo hồ sơ khách hàng và lưu vào CSDL.",
          "Hệ thống hiển thị thông báo thành công kèm mã khách hàng mới."
        ],
        alt: [
          "A1. Khách hàng đã tồn tại (CCCD trùng): Hệ thống thông báo lỗi và yêu cầu kiểm tra lại.",
          "A2. Khách hàng chưa đủ 18 tuổi: Hệ thống từ chối và thông báo không đủ điều kiện.",
          "A3. Thông tin thiếu hoặc không hợp lệ: Hệ thống yêu cầu nhập lại các trường bị lỗi."
        ],
        post: [
          "Hồ sơ khách hàng được tạo thành công với trạng thái hoạt động (active).",
          "Mã khách hàng được sinh tự động và trả về cho giao dịch viên."
        ]
      },
      {
        name: "Khóa Hồ Sơ Khách Hàng",
        code: "UC-CS-02",
        actors: "Giao dịch viên",
        goal: "Vô hiệu hóa hồ sơ khách hàng khi khách hàng yêu cầu rời khỏi ngân hàng.",
        pre: [
          "Giao dịch viên đã đăng nhập vào hệ thống.",
          "Khách hàng đã có hồ sơ hợp lệ và đang hoạt động trong hệ thống.",
          "Tất cả tài khoản của khách hàng đã được đóng và số dư bằng 0."
        ],
        main: [
          'Giao dịch viên chọn chức năng "Khóa Hồ Sơ Khách Hàng".',
          "Hệ thống yêu cầu cung cấp số CCCD của khách hàng.",
          "Giao dịch viên nhập CCCD và xác nhận.",
          "Hệ thống tìm kiếm khách hàng theo CCCD.",
          "Hệ thống kiểm tra trạng thái tất cả tài khoản liên kết của khách hàng.",
          'Hệ thống cập nhật trạng thái hồ sơ khách hàng thành "inactive".',
          "Hệ thống hiển thị thông báo khóa hồ sơ thành công."
        ],
        alt: [
          "A1. Không tìm thấy khách hàng: Hệ thống thông báo không tìm thấy hồ sơ.",
          "A2. Khách hàng còn tài khoản chưa đóng hoặc còn số dư: Hệ thống từ chối và yêu cầu đóng/rút hết tiền trước."
        ],
        post: [
          'Hồ sơ khách hàng được cập nhật trạng thái thành "inactive".',
          "Khách hàng không thể thực hiện giao dịch sau khi hồ sơ bị khóa."
        ]
      },
      {
        name: "Tra Cứu Thông Tin Khách Hàng",
        code: "UC-CS-03",
        actors: "Giao dịch viên",
        goal: "Tra cứu và hiển thị thông tin chi tiết của một khách hàng trong hệ thống.",
        pre: [
          "Giao dịch viên đã đăng nhập vào hệ thống.",
          "Khách hàng cần tra cứu đã có hồ sơ trong hệ thống."
        ],
        main: [
          'Giao dịch viên chọn chức năng "Tra Cứu Thông Tin Khách Hàng".',
          "Hệ thống yêu cầu nhập CCCD hoặc mã khách hàng.",
          "Giao dịch viên nhập thông tin tìm kiếm.",
          "Hệ thống tra cứu và hiển thị thông tin chi tiết: họ tên, CCCD, ngày sinh, địa chỉ, danh sách tài khoản liên kết.",
          "Giao dịch viên xem và sử dụng thông tin khi cần."
        ],
        alt: [
          "A1. Không tìm thấy khách hàng: Hệ thống thông báo không có kết quả khớp với điều kiện tìm kiếm."
        ],
        post: [
          "Thông tin chi tiết của khách hàng được hiển thị thành công."
        ]
      }
    ]
  },
  {
    heading: "2.3.2. Quản Lý Tài Khoản",
    ucs: [
      {
        name: "Mở Tài Khoản",
        code: "UC-TK-01",
        actors: "Giao dịch viên",
        goal: "Tạo một tài khoản ngân hàng mới cho khách hàng đã có hồ sơ hợp lệ.",
        pre: [
          "Giao dịch viên đã đăng nhập vào hệ thống.",
          "Khách hàng đã có hồ sơ hợp lệ và đang ở trạng thái hoạt động (active).",
          "Số tài khoản cần tạo chưa tồn tại trong hệ thống."
        ],
        main: [
          'Giao dịch viên chọn chức năng "Mở Tài Khoản".',
          "Hệ thống yêu cầu nhập: CCCD khách hàng, số tài khoản, mật khẩu tài khoản, và số dư ban đầu.",
          "Giao dịch viên nhập thông tin và xác nhận.",
          "Hệ thống kiểm tra tính hợp lệ của thông tin đầu vào.",
          "Hệ thống tạo tài khoản với trạng thái \"open\" và lưu vào CSDL.",
          "Nếu có số dư ban đầu > 0, hệ thống tự động ghi nhận giao dịch gửi tiền (deposit) tương ứng.",
          "Hệ thống hiển thị thông báo thành công kèm số tài khoản và số dư ban đầu."
        ],
        alt: [
          "A1. Số dư ban đầu âm (< 0): Hệ thống báo lỗi và yêu cầu nhập lại.",
          "A2. Khách hàng không tồn tại hoặc đã bị khóa: Hệ thống từ chối tạo tài khoản.",
          "A3. Số tài khoản đã tồn tại: Hệ thống thông báo xung đột và yêu cầu dùng số tài khoản khác."
        ],
        post: [
          'Tài khoản mới được tạo với trạng thái "open" và ngày mở được ghi nhận.',
          "Số dư ban đầu được ghi nhận thông qua giao dịch deposit (nếu có)."
        ]
      },
      {
        name: "Đóng Tài Khoản",
        code: "UC-TK-02",
        actors: "Giao dịch viên",
        goal: "Đóng một tài khoản ngân hàng đang hoạt động theo yêu cầu của khách hàng.",
        pre: [
          "Giao dịch viên đã đăng nhập vào hệ thống.",
          'Tài khoản cần đóng đang ở trạng thái "open" và thuộc sở hữu của khách hàng.',
          "Số dư tài khoản bằng 0 (khách hàng đã rút toàn bộ tiền)."
        ],
        main: [
          'Giao dịch viên chọn chức năng "Đóng Tài Khoản".',
          "Hệ thống yêu cầu nhập CCCD của khách hàng và số tài khoản cần đóng.",
          "Giao dịch viên nhập thông tin và xác nhận.",
          "Hệ thống xác minh quyền sở hữu tài khoản và kiểm tra số dư.",
          'Hệ thống cập nhật trạng thái tài khoản thành "closed" và ghi nhận ngày đóng.',
          "Hệ thống hiển thị thông báo đóng tài khoản thành công."
        ],
        alt: [
          "A1. Khách hàng không tồn tại: Hệ thống thông báo lỗi.",
          'A2. Tài khoản không tồn tại hoặc không ở trạng thái "open": Hệ thống từ chối.',
          "A3. Tài khoản còn số dư: Hệ thống yêu cầu rút hết tiền trước khi thực hiện đóng.",
          "A4. Tài khoản không thuộc quyền sở hữu của khách hàng: Hệ thống từ chối."
        ],
        post: [
          'Trạng thái tài khoản được cập nhật thành "closed".',
          "Ngày đóng tài khoản được ghi nhận vào CSDL."
        ]
      }
    ]
  },
  {
    heading: "2.3.3. Xử Lý Giao Dịch",
    ucs: [
      {
        name: "Chuyển Khoản Nội Bộ",
        code: "UC-GD-01",
        actors: "Khách hàng",
        goal: "Chuyển tiền từ tài khoản nguồn sang tài khoản đích trong cùng hệ thống ngân hàng.",
        pre: [
          "Khách hàng đã đăng nhập vào hệ thống.",
          'Tài khoản nguồn và tài khoản đích đều tồn tại và đang ở trạng thái "open".',
          "Tài khoản nguồn khác tài khoản đích.",
          "Tài khoản nguồn có đủ số dư để thực hiện giao dịch."
        ],
        main: [
          'Khách hàng chọn chức năng "Chuyển Khoản Nội Bộ".',
          "Hệ thống yêu cầu nhập: số tài khoản đích, số tiền, nội dung chuyển khoản.",
          "Khách hàng nhập thông tin và xác nhận giao dịch.",
          "Hệ thống kiểm tra tính hợp lệ: số dư, trạng thái các tài khoản, điều kiện giao dịch.",
          "Hệ thống trừ tiền từ tài khoản nguồn và cộng vào tài khoản đích (atomic operation).",
          "Hệ thống ghi nhận giao dịch vào nhật ký (bảng trans + in_bank_trans).",
          "Hệ thống hiển thị thông báo thành công kèm mã giao dịch."
        ],
        alt: [
          "A1. Tài khoản đích không tồn tại hoặc đã đóng: Hệ thống từ chối và thông báo lỗi.",
          "A2. Tài khoản nguồn trùng tài khoản đích: Hệ thống từ chối thực hiện giao dịch.",
          "A3. Số dư không đủ: Hệ thống thông báo số dư không đủ và từ chối.",
          "A4. Số tiền không hợp lệ (≤ 0): Hệ thống báo lỗi và yêu cầu nhập lại."
        ],
        post: [
          "Số dư tài khoản nguồn giảm đúng số tiền đã chuyển.",
          "Số dư tài khoản đích tăng đúng số tiền đã chuyển.",
          'Giao dịch được ghi nhận với trạng thái "finished".'
        ]
      },
      {
        name: "Chuyển Khoản Liên Ngân Hàng",
        code: "UC-GD-02",
        actors: "Khách hàng",
        goal: "Chuyển tiền từ tài khoản trong ngân hàng sang tài khoản thuộc ngân hàng bên ngoài.",
        pre: [
          "Khách hàng đã đăng nhập vào hệ thống.",
          'Tài khoản nguồn tồn tại và đang ở trạng thái "open".',
          "Tài khoản nguồn có đủ số dư để thực hiện giao dịch."
        ],
        main: [
          'Khách hàng chọn chức năng "Chuyển Khoản Liên Ngân Hàng".',
          "Hệ thống yêu cầu nhập: tên/chi nhánh ngân hàng đích, số tài khoản đích, số tiền, nội dung.",
          "Khách hàng nhập thông tin và xác nhận giao dịch.",
          "Hệ thống kiểm tra số dư tài khoản nguồn.",
          "Hệ thống trừ tiền từ tài khoản nguồn và ghi nhận giao dịch (bảng trans + out_bank_trans).",
          "Hệ thống chuyển yêu cầu đến ngân hàng đích để xử lý phía nhận.",
          "Hệ thống hiển thị thông báo thành công kèm mã giao dịch."
        ],
        alt: [
          "A1. Số dư không đủ: Hệ thống thông báo và từ chối giao dịch.",
          "A2. Thông tin ngân hàng đích không hợp lệ: Hệ thống báo lỗi và yêu cầu kiểm tra lại.",
          "A3. Số tiền không hợp lệ (≤ 0): Hệ thống báo lỗi."
        ],
        post: [
          "Số dư tài khoản nguồn giảm đúng số tiền đã chuyển.",
          "Giao dịch được ghi nhận với thông tin ngân hàng đích đầy đủ."
        ]
      },
      {
        name: "Gửi Tiền Trực Tiếp (Deposit)",
        code: "UC-GD-03",
        actors: "Khách hàng, Giao dịch viên",
        goal: "Giao dịch viên tiếp nhận tiền mặt từ khách hàng và cộng vào tài khoản chỉ định.",
        pre: [
          'Giao dịch viên đã đăng nhập và đang ở trạng thái "active" (đang làm việc).',
          'Tài khoản đích tồn tại và đang ở trạng thái "open".',
          "Số tiền gửi lớn hơn 0."
        ],
        main: [
          'Giao dịch viên chọn chức năng "Gửi Tiền".',
          "Hệ thống yêu cầu nhập: số tài khoản đích và số tiền.",
          "Giao dịch viên nhập thông tin, nhận tiền mặt từ khách hàng và xác nhận.",
          "Hệ thống kiểm tra tài khoản hợp lệ và cộng tiền vào số dư.",
          "Hệ thống ghi nhận giao dịch kèm mã giao dịch viên xử lý (bảng trans + deposit).",
          "Hệ thống hiển thị thông báo thành công kèm mã giao dịch và số dư mới."
        ],
        alt: [
          "A1. Tài khoản không tồn tại hoặc đã đóng: Hệ thống từ chối.",
          'A2. Giao dịch viên không ở trạng thái "active": Hệ thống từ chối thực hiện giao dịch.',
          "A3. Số tiền không hợp lệ (≤ 0): Hệ thống báo lỗi và yêu cầu nhập lại."
        ],
        post: [
          "Số dư tài khoản tăng đúng số tiền đã gửi.",
          "Giao dịch được ghi nhận kèm mã giao dịch viên và thời gian thực hiện."
        ]
      },
      {
        name: "Rút Tiền Trực Tiếp (Withdrawal)",
        code: "UC-GD-04",
        actors: "Khách hàng, Giao dịch viên",
        goal: "Giao dịch viên xử lý yêu cầu rút tiền mặt từ tài khoản của khách hàng.",
        pre: [
          'Giao dịch viên đã đăng nhập và đang ở trạng thái "active" (đang làm việc).',
          'Tài khoản nguồn tồn tại và đang ở trạng thái "open".',
          "Số tiền rút nhỏ hơn hoặc bằng số dư hiện có của tài khoản."
        ],
        main: [
          'Giao dịch viên chọn chức năng "Rút Tiền".',
          "Hệ thống yêu cầu nhập: số tài khoản và số tiền cần rút.",
          "Giao dịch viên nhập thông tin và xác nhận.",
          "Hệ thống kiểm tra số dư và khóa hàng (FOR UPDATE) để tránh xung đột đồng thời.",
          "Hệ thống khấu trừ số tiền từ tài khoản.",
          "Giao dịch viên trao tiền mặt cho khách hàng.",
          "Hệ thống ghi nhận giao dịch kèm mã giao dịch viên (bảng trans + withdraw).",
          "Hệ thống hiển thị thông báo thành công kèm mã giao dịch và số dư còn lại."
        ],
        alt: [
          "A1. Tài khoản không tồn tại hoặc đã đóng: Hệ thống từ chối.",
          'A2. Giao dịch viên không ở trạng thái "active": Hệ thống từ chối thực hiện giao dịch.',
          "A3. Số dư không đủ: Hệ thống thông báo số dư không đủ và từ chối.",
          "A4. Số tiền không hợp lệ (≤ 0): Hệ thống báo lỗi."
        ],
        post: [
          "Số dư tài khoản giảm đúng số tiền đã rút.",
          "Giao dịch được ghi nhận kèm mã giao dịch viên và thời gian thực hiện."
        ]
      },
      {
        name: "Thanh Toán Hóa Đơn",
        code: "UC-GD-05",
        actors: "Khách hàng",
        goal: "Thanh toán các hóa đơn dịch vụ (điện, nước, internet, bảo hiểm,...) trực tiếp từ tài khoản ngân hàng.",
        pre: [
          "Khách hàng đã đăng nhập vào hệ thống.",
          'Tài khoản thanh toán tồn tại và đang ở trạng thái "open".',
          "Tài khoản có đủ số dư để thanh toán hóa đơn."
        ],
        main: [
          'Khách hàng chọn chức năng "Thanh Toán Hóa Đơn".',
          "Hệ thống hiển thị danh sách loại hóa đơn có thể thanh toán.",
          "Khách hàng chọn loại hóa đơn và nhập số tiền cần thanh toán.",
          "Khách hàng xác nhận giao dịch.",
          "Hệ thống trừ tiền từ tài khoản và ghi nhận giao dịch (bảng trans + bill).",
          "Hệ thống hiển thị thông báo thanh toán thành công kèm mã giao dịch."
        ],
        alt: [
          "A1. Tài khoản không tồn tại hoặc đã đóng: Hệ thống từ chối.",
          "A2. Số dư không đủ: Hệ thống thông báo số dư không đủ để thanh toán.",
          "A3. Số tiền không hợp lệ (≤ 0): Hệ thống báo lỗi và yêu cầu nhập lại."
        ],
        post: [
          "Số dư tài khoản giảm đúng số tiền đã thanh toán.",
          "Giao dịch được ghi nhận với loại hóa đơn tương ứng."
        ]
      }
    ]
  },
  {
    heading: "2.3.4. Tra Cứu & Báo Cáo",
    ucs: [
      {
        name: "Kiểm Tra Trạng Thái Giao Dịch",
        code: "UC-BC-01",
        actors: "Khách hàng",
        goal: "Tra cứu và xem trạng thái hiện tại của một giao dịch cụ thể.",
        pre: [
          "Khách hàng đã đăng nhập vào hệ thống.",
          'Tài khoản ngân hàng tồn tại và đang ở trạng thái "open".'
        ],
        main: [
          'Khách hàng chọn chức năng "Kiểm Tra Trạng Thái Giao Dịch".',
          "Hệ thống yêu cầu nhập mã giao dịch cần tra cứu.",
          "Khách hàng nhập mã giao dịch.",
          "Hệ thống tra cứu và hiển thị: loại giao dịch, số tiền, thời gian, trạng thái (Hoàn Thành / Đã Hủy)."
        ],
        alt: [
          "A1. Tài khoản/Mật khẩu sai khi đăng nhập: Hệ thống yêu cầu đăng nhập lại.",
          "A2. Mã giao dịch không tồn tại hoặc không thuộc tài khoản này: Hệ thống thông báo không tìm thấy."
        ],
        post: [
          "Thông tin và trạng thái giao dịch được hiển thị thành công."
        ]
      },
      {
        name: "Xem Lịch Sử Giao Dịch",
        code: "UC-BC-02",
        actors: "Khách hàng",
        goal: "Xem danh sách toàn bộ giao dịch đã thực hiện của tài khoản, sắp xếp theo thứ tự thời gian.",
        pre: [
          "Khách hàng đã đăng nhập vào hệ thống.",
          "Tài khoản ngân hàng tồn tại trong hệ thống."
        ],
        main: [
          "Khách hàng đăng nhập vào hệ thống.",
          'Khách hàng chọn chức năng "Lịch Sử Giao Dịch".',
          "Hệ thống hiển thị toàn bộ lịch sử giao dịch theo thứ tự thời gian giảm dần (mới nhất trước).",
          "Khách hàng có thể lọc theo: loại giao dịch, chiều giao dịch (vào/ra), khoảng thời gian."
        ],
        alt: [
          "A1. Tài khoản/Mật khẩu sai khi đăng nhập: Hệ thống yêu cầu đăng nhập lại.",
          "A2. Tài khoản chưa có giao dịch nào: Hệ thống thông báo chưa có lịch sử giao dịch."
        ],
        post: [
          "Danh sách giao dịch được hiển thị thành công, sắp xếp theo thứ tự thời gian."
        ]
      },
      {
        name: "Thống Kê Giao Dịch",
        code: "UC-BC-03",
        actors: "Khách hàng",
        goal: "Xem thống kê tổng hợp số tiền vào/ra theo khoảng thời gian và đơn vị tùy chọn.",
        pre: [
          "Khách hàng đã đăng nhập vào hệ thống.",
          "Tài khoản ngân hàng tồn tại và đang hoạt động."
        ],
        main: [
          "Khách hàng đăng nhập và chọn chức năng \"Thống Kê Giao Dịch\".",
          "Hệ thống yêu cầu chọn mốc thời gian bắt đầu và kết thúc.",
          "Khách hàng chọn đơn vị thời gian hiển thị (ngày / tháng / năm).",
          "Hệ thống tổng hợp và hiển thị: tổng tiền vào, tổng tiền ra, số dư đầu kỳ và cuối kỳ."
        ],
        alt: [
          "A1. Tài khoản/Mật khẩu sai khi đăng nhập: Hệ thống yêu cầu đăng nhập lại.",
          "A2. Khoảng thời gian không hợp lệ (ngày bắt đầu sau ngày kết thúc): Hệ thống báo lỗi."
        ],
        post: [
          "Bảng thống kê giao dịch được hiển thị thành công theo khoảng thời gian đã chọn."
        ]
      },
      {
        name: "Sao Kê Tài Khoản",
        code: "UC-BC-04",
        actors: "Giao dịch viên",
        goal: "Xem sao kê đầy đủ của tài khoản và xác minh số dư thực tế khớp với lịch sử giao dịch tích lũy.",
        pre: [
          "Giao dịch viên đã đăng nhập vào hệ thống.",
          "Tài khoản cần sao kê tồn tại trong hệ thống."
        ],
        main: [
          'Giao dịch viên chọn chức năng "Sao Kê Tài Khoản".',
          "Hệ thống yêu cầu nhập số tài khoản.",
          "Giao dịch viên nhập số tài khoản.",
          "Hệ thống trả về sao kê đầy đủ: tổng tiền vào, tổng tiền ra, số dư hiện tại.",
          "Hệ thống so sánh và xác nhận số dư hiện tại khớp với tổng hợp giao dịch (Đúng / Sai)."
        ],
        alt: [
          "A1. Tài khoản không tồn tại: Hệ thống thông báo lỗi.",
          "A2. Số dư không khớp với lịch sử giao dịch (bất thường): Hệ thống cảnh báo và đánh dấu cần kiểm tra."
        ],
        post: [
          "Sao kê tài khoản được hiển thị và kết quả đối chiếu được trả về thành công."
        ]
      },
      {
        name: "Báo Cáo Giao Dịch Theo Thời Gian",
        code: "UC-BC-05",
        actors: "Giao dịch viên, Quản lý chi nhánh",
        goal: "Xem báo cáo tổng hợp số lượng và tổng giá trị giao dịch theo đơn vị thời gian tại một chi nhánh.",
        pre: [
          "Giao dịch viên hoặc quản lý đã đăng nhập vào hệ thống.",
          "Có dữ liệu giao dịch trong khoảng thời gian và chi nhánh được chọn."
        ],
        main: [
          'Người dùng chọn chức năng "Báo Cáo Giao Dịch Theo Thời Gian".',
          "Hệ thống yêu cầu chọn: chi nhánh, khoảng thời gian, đơn vị báo cáo (giờ / ngày / tháng / năm).",
          "Người dùng chọn các tiêu chí và xác nhận.",
          "Hệ thống tổng hợp và trả về báo cáo: số lượng giao dịch, tổng giá trị, phân loại theo từng loại giao dịch."
        ],
        alt: [
          "A1. Không có dữ liệu giao dịch trong khoảng thời gian đã chọn: Hệ thống thông báo không có dữ liệu.",
          "A2. Chi nhánh được chọn không tồn tại: Hệ thống thông báo lỗi."
        ],
        post: [
          "Báo cáo giao dịch được tổng hợp và hiển thị thành công theo các tiêu chí đã chọn."
        ]
      }
    ]
  }
];

// ─── BUILD DOCUMENT ────────────────────────────────────────────────────────────
const children = [
  // Document title
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 120 },
    children: [run("NGÂN HÀNG VCB – HỆ THỐNG QUẢN LÝ GIAO DỊCH", { bold: true, size: 28, color: NAVY })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 80 },
    children: [run("TÀI LIỆU ĐẶC TẢ CHỨC NĂNG", { bold: true, size: 32, color: BLUE })]
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 80 },
    children: [run("Phiên bản 1.0 — 2025", { size: 20, color: "595959", italics: true })]
  }),
  new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BLUE, space: 4 } },
    spacing: { after: 480 },
    children: [run("")]
  }),

  // Section heading
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 0, after: 200 },
    children: [run("2.3. Đặc Tả Các Chức Năng", { bold: true, size: 30, color: NAVY })]
  }),
  new Paragraph({
    spacing: { after: 400 },
    children: [run(
      "Phần này mô tả chi tiết các ca sử dụng (use case) của hệ thống ngân hàng, bao gồm: tác nhân tham gia, mục tiêu nghiệp vụ, tiền điều kiện, luồng sự kiện chính, các luồng rẽ nhánh xử lý lỗi, và hậu điều kiện sau khi thực hiện thành công.",
      { italics: true, color: "595959" }
    )]
  }),
];

// Generate each section
for (const section of SECTIONS) {
  children.push(
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 400, after: 200 },
      children: [run(section.heading, { bold: true, size: 26, color: BLUE })]
    })
  );

  for (const uc of section.ucs) {
    children.push(
      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 320, after: 120 },
        children: [run(`${uc.code}  —  ${uc.name}`, { bold: true, size: 23, color: NAVY })]
      }),
      ucTable(uc),
      gap()
    );
  }
}

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Times New Roman", size: 22 } }
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Times New Roman", size: 30, bold: true, color: NAVY },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Times New Roman", size: 26, bold: true, color: BLUE },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 1 }
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: "Times New Roman", size: 23, bold: true, color: NAVY },
        paragraph: { spacing: { before: 300, after: 120 }, outlineLevel: 2 }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1080, bottom: 1440, left: 1440 }
      }
    },
    children
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('/mnt/user-data/outputs/dac_ta_chuc_nang.docx', buf);
  console.log('Done! File written.');
});