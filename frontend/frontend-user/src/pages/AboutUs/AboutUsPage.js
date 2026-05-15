import React from "react";
import "./AboutUsPage.scss";

function AboutUsPage() {
  const teamMembers = [
    { initials: "M1", name: "Member1", role: "role" },
    { initials: "M2", name: "Member2", role: "role" },
    { initials: "M3", name: "Member3", role: "role" },
    { initials: "M4", name: "Member4", role: "role" },
    { initials: "M5", name: "Member5", role: "role" },
    { initials: "M6", name: "Member6", role: "role" },
  ];

  return (
    <div className="about">
      {/* SECTION: HERO */}
      <section className="about__hero">
        <div className="about__container">
          <div className="about__hero-content">
            <h1 className="about__title">AI Translation Project</h1>
            <p className="about__body">
              Chúng tôi là nhóm 6 sinh viên đam mê công nghệ, xây dựng công cụ
              dịch thuật giúp việc chuyển đổi Anh - Việt trở nên chính xác, tự
              nhiên và tối ưu nhất cho người dùng Việt.
            </p>

            <div className="about__stats">
              <div className="about__stat-item">
                <div className="about__stat-value">Tên model</div>
                <div className="about__stat-label">Công nghệ cốt lõi</div>
              </div>
              <div className="about__stat-sep"></div>
              <div className="about__stat-item">
                <div className="about__stat-value">...</div>
                <div className="about__stat-label">Độ chính xác</div>
              </div>
              <div className="about__stat-sep"></div>
              <div className="about__stat-item">
                <div className="about__stat-value">24/7</div>
                <div className="about__stat-label">Sẵn sàng hỗ trợ</div>
              </div>
            </div>
          </div>

          <div className="about__hero-visual">
            <div className="about__glass-card">
              <div className="about__glass-header">
                <div className="about__dot"></div>
                <div className="about__dot"></div>
                <div className="about__dot"></div>
              </div>
              <div className="about__glass-content">
                <div className="about__lang-tag">English</div>
                <div className="about__translate-icon">⇄</div>
                <div className="about__lang-tag is-vi">Tiếng Việt</div>
              </div>
              <div className="about__pulse-line"></div>
              <div className="about__pulse-line short"></div>
            </div>
            <div className="about__blob"></div>
          </div>
        </div>
      </section>

      {/* SECTION: FEATURES */}
      <section className="about__features">
        <div className="about__container">
          <div className="about__section-head">
            <h2 className="about__section-title">Ứng dụng cốt lõi</h2>
          </div>

          <div className="about__feature-grid">
            {[
              {
                icon: "bx bx-edit-alt",
                title: "Dịch văn bản",
                desc: "Xử lý tức thì các đoạn văn bản dài với ngữ pháp chuẩn xác.",
              },
              {
                icon: "bx bx-file",
                title: "Dịch file PDF",
                desc: "Giữ nguyên định dạng, bảng biểu và hình ảnh của tài liệu gốc.",
              },
              {
                icon: "bx bx-bolt-circle",
                title: "Tốc độ vượt trội",
                desc: "Tối ưu hóa thời gian phản hồi, nhận kết quả chỉ trong vài giây.",
              },
            ].map((feat, i) => (
              <div className="about__feature-card" key={i}>
                <div className="about__feature-icon">
                  <i className={feat.icon}></i>{" "}
                </div>
                <h3 className="about__feature-name">{feat.title}</h3>
                <p className="about__feature-desc">{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SECTION: TEAM */}
      <section className="about__team">
        <div className="about__container">
          <div className="about__section-head is-light">
            <h2 className="about__section-title">Đội ngũ phát triển</h2>
          </div>

          <div className="about__team-grid">
            {teamMembers.map((member, i) => (
              <div className="about__member-card" key={i}>
                <div className="about__member-avatar">{member.initials}</div>
                <div className="about__member-info">
                  <h4 className="about__member-name">{member.name}</h4>
                  <span className="about__member-role">{member.role}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

export default AboutUsPage;
