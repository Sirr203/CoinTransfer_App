# Xu Gọn (Ứng dụng Tối Ưu Tiền Xu tại Nhật)

Ứng dụng hỗ trợ gợi ý cách trả tiền mặt tại quầy (Conbini, siêu thị, nhà hàng...) sao cho ví nhẹ nhất sau giao dịch. Hoạt động 100% offline, lưu trữ nội bộ bằng file JSON.

---

## ✨ Điểm mới trong bản cập nhật (Update 1)

1. **Giao diện SafeArea & Theme Teal:** Toàn bộ giao diện nằm trong `SafeArea`, không bị tràn viền hay đè lên status bar / thanh cử chỉ. Dùng theme màu teal hiện đại.
2. **Thanh điều hướng dưới đáy (NavigationBar):** Chuyển giữa màn **Ví** và **Trả tiền** dễ dàng bằng 1 tay.
3. **Màn mặc định là Ví:** Mở app hiển thị ngay tổng tiền và danh sách thẻ ví. Khi bấm sang **Trả tiền**, ô hóa đơn tự focus để gõ ngay.
4. **Nhập số lượng linh hoạt:** Chạm trực tiếp vào ô số của từng mệnh giá để gõ bàn phím số, hoặc dùng nút `+` / `-`. Hiển thị thành tiền từng mệnh giá.
5. **Khối kết quả trực quan:** Phân chia rõ ràng thành 2 khối màu:
   - **ĐƯA:** Màu xanh teal nổi bật với tổng tiền và từng loại tờ/xu.
   - **NHẬN LẠI:** Màu xanh dương thể hiện số tiền thối lại.
6. **2 Chế độ tính toán:**
   - **Mặc định (Nhanh):** Đưa & nhận lại ít tờ/xu nhất (hóa đơn 10¥ chỉ đưa 1 xu 10¥, không thối).
   - **Công tắc "Tối ưu tiền giấy":** Ưu tiên tống khứ xu lẻ để dọn sạch ví, tự động lưu lựa chọn cho các lần sau.
7. **Icon ứng dụng mới:** Đồng xu vàng với biểu tượng ¥ trên nền teal tại `src/assets/icon.png`.
8. **Tự động tăng Build Number:** Thêm cờ `--build-number` vào GitHub Actions để mỗi lần build có số phiên bản tăng dần.

---

## 📁 Cấu trúc thư mục

- `src/core.py`: Thuật toán quy hoạch động với 2 chế độ và lưu trữ `wallet.json`, `settings.json`.
- `src/main.py`: Giao diện Flet 0.28 (SafeArea, NavigationBar, Theme Teal).
- `src/assets/icon.png`: Icon launcher của ứng dụng (đồng xu vàng chữ ¥ nền teal).
- `src/test_core.py`: Unit test thuật toán 2 chế độ.
- `pyproject.toml`: Cấu hình app "Xu Gọn" và build Flet.
- `.github/workflows/build-apk.yml`: Tự động build APK trên GitHub Actions.
