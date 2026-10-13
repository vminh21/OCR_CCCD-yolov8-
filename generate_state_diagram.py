import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set high-DPI figure
fig, ax = plt.subplots(figsize=(6.8, 14.5), dpi=300)
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

# Dimensions
bw, bh = 2.4, 0.68

# Coordinates (x, y)
states = {
    "start": (3.4, 13.5),
    "cho_nd": (3.4, 12.1),
    "dang_nd": (3.4, 10.3),
    "khong_hl": (1.75, 8.6),
    "thanh_cong": (4.8, 7.3),
    "bat_dau_tx": (3.4, 5.6),
    "trich_xuat_tc": (3.4, 3.9),
    "hien_thi": (3.4, 2.3),
    "hoan_thanh": (3.4, 0.85),
    "end": (3.4, -0.15)
}

# 1. Initial State (filled black circle)
start_circle = plt.Circle(states["start"], 0.16, color='black', ec='black', zorder=5)
ax.add_patch(start_circle)

# 2. Final State (bullseye: circle inside circle)
end_outer = plt.Circle(states["end"], 0.18, color='none', ec='black', lw=2.0, zorder=5)
end_inner = plt.Circle(states["end"], 0.11, color='black', ec='black', zorder=6)
ax.add_patch(end_outer)
ax.add_patch(end_inner)

# Function to draw rounded rect state box
def draw_state(center, text, w=bw, h=bh):
    x = center[0] - w/2
    y = center[1] - h/2
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.08,rounding_size=0.15",
        ec="black", fc="white", lw=1.6, zorder=4
    )
    ax.add_patch(box)
    ax.text(center[0], center[1], text, ha='center', va='center',
            fontsize=11.5, fontweight='500', family='sans-serif', color='black', zorder=6)

# Draw state boxes
draw_state(states["cho_nd"], "Chờ nhận diện")
draw_state(states["dang_nd"], "Đang nhận diện")
draw_state(states["khong_hl"], "Nhận diện không\nhợp lệ", w=2.45, h=0.78)
draw_state(states["thanh_cong"], "Nhận diện thành\ncông", w=2.45, h=0.78)
draw_state(states["bat_dau_tx"], "Bắt đầu trích xuất")
draw_state(states["trich_xuat_tc"], "Trích xuất hoàn tất")
draw_state(states["hien_thi"], "Hiển thị thông tin\nchi tiết", w=2.45, h=0.78)
draw_state(states["hoan_thanh"], "Hoàn thành")

# Helper for drawing transition arrows
def draw_arrow(p1, p2, label="", label_pos=(0,0), rad=0.0, ha='center', va='center'):
    arrow = patches.FancyArrowPatch(
        p1, p2,
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>,head_length=7,head_width=4.5",
        color="black", lw=1.4, zorder=3
    )
    ax.add_patch(arrow)
    if label:
        ax.text(label_pos[0], label_pos[1], label, ha=ha, va=va,
                fontsize=10, color='black', backgroundcolor='white',
                family='sans-serif', zorder=7)

# 1. start -> cho_nd
draw_arrow((3.4, 13.34), (3.4, 12.44))

# 2. cho_nd -> dang_nd
draw_arrow((3.4, 11.76), (3.4, 10.64), label="Bắt đầu chụp / tải", label_pos=(3.4, 11.2))

# 3. dang_nd -> khong_hl (mờ/chói)
draw_arrow((2.65, 9.96), (1.75, 8.99), label="Ảnh mờ / chói sáng", label_pos=(1.5, 9.75), rad=-0.08, ha='center')

# 4. khong_hl -> dang_nd (chụp lại)
draw_arrow((2.2, 8.99), (3.15, 9.96), label="Chụp lại", label_pos=(3.15, 9.35), rad=-0.06, ha='left')

# 5. dang_nd -> thanh_cong (hợp lệ - cong sang phải)
draw_arrow((4.6, 10.3), (4.8, 7.7), label="Hợp lệ", label_pos=(5.4, 9.2), rad=-0.38)

# 6. khong_hl -> thanh_cong (sửa thủ công)
draw_arrow((1.75, 8.21), (3.57, 7.3), label="Sửa thủ công", label_pos=(2.2, 7.4), rad=-0.22)

# 7. thanh_cong -> bat_dau_tx (nhấn trích xuất)
draw_arrow((4.4, 6.91), (3.8, 5.99), label="Nhấn trích xuất", label_pos=(4.55, 6.45), rad=0.08)

# 8. bat_dau_tx -> trich_xuat_tc (tính toán xong)
draw_arrow((3.4, 5.26), (3.4, 4.29), label="Tính toán xong", label_pos=(3.4, 4.78))

# 9. trich_xuat_tc -> hien_thi (xem kết quả)
draw_arrow((3.4, 3.56), (3.4, 2.69), label="Xem hướng dẫn / kết quả", label_pos=(3.4, 3.12))

# 10. hien_thi -> hoan_thanh (xử lý xong)
draw_arrow((3.4, 1.91), (3.4, 1.19), label="Xử lý xong", label_pos=(3.4, 1.55))

# 11. hoan_thanh -> end
draw_arrow((3.4, 0.51), (3.4, 0.03))

# Plot settings
ax.set_xlim(0, 6.8)
ax.set_ylim(-0.6, 14.0)
ax.axis('off')

plt.tight_layout()
plt.savefig("state_diagram.png", dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig("state_diagram.svg", bbox_inches='tight', facecolor='white')
print("State diagram updated successfully.")
