# Xu Optimizer (Ứng dụng Tối Ưu Tiền Xu tại Nhật)

Ứng dụng hỗ trợ gợi ý cách trả tiền mặt tại quầy (Conbini, siêu thị, nhà hàng...) sao cho ví nhẹ nhất sau giao dịch, ưu tiên tống khứ các đồng xu lẻ và hạn chế nhận thêm xu thối lại. Hoạt động 100% offline, lưu trữ nội bộ bằng file JSON.

---

## 📁 Cấu trúc thư mục

- `src/core.py`: Thuật toán quy hoạch động (DP knapsack) gợi ý số tiền đưa tối ưu và cơ chế đọc/ghi `wallet.json`.
- `src/main.py`: Giao diện ứng dụng viết bằng Flet (Tab Ví & Tab Trả tiền).
- `src/test_core.py`: Unit test thuật toán `core.py`.
- `pyproject.toml`: Cấu hình ứng dụng và thông số build Flet.
- `.github/workflows/build-apk.yml`: CI/CD tự động build file APK Android mỗi khi push lên nhánh `main`.

---

## 🚀 Đẩy code lên GitHub & Tự động Build APK

1. **Khởi tạo và đẩy code lên GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Xu Optimizer"
   git branch -M main
   git remote add origin https://github.com/<tai-khoan-cua-ban>/<ten-repo>.git
   git push -u origin main
   ```

2. **Tải file APK từ GitHub Actions:**
   - Truy cập vào repo của bạn trên GitHub.
   - Nhấp vào tab **Actions**.
   - Bấm vào workflow chạy gần nhất (mang tên commit của bạn).
   - Cuộn xuống phần **Artifacts** ở đáy trang.
   - Bấm tải file `xu-optimizer-apk` (file tải về ở dạng `.zip`).
   - Giải nén file `.zip` để lấy file `.apk` và cài đặt lên điện thoại Android.

---

## 🛠️ Chạy thử trên máy tính (Local)

Nếu môi trường máy tính đã cài đặt Python:
```bash
pip install flet==0.28.3
python src/main.py
```

Chạy test thuật toán:
```bash
python src/test_core.py
```
