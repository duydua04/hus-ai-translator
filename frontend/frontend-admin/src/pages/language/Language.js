import React, { useState } from "react";
import Badge from "../../components/common/Badge";
import Pagination from "../../components/common/Pagination";
import AddLanguageForm from "./AddLanguage/AddLanguage";
import useLanguage from "../../hooks/useLaguage";
import "./Language.scss";

const PAGE_SIZE = 10;

export default function LanguagesPage() {
  const { languages, loading, error, createLanguage, toggleLanguage } =
    useLanguage();

  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);

  const filtered = languages.filter((lang) => {
    const matchSearch =
      lang.language_name.toLowerCase().includes(search.toLowerCase()) ||
      lang.language_code.toLowerCase().includes(search.toLowerCase());
    const matchStatus =
      filterStatus === ""
        ? true
        : filterStatus === "active"
        ? lang.is_active
        : !lang.is_active;
    return matchSearch && matchStatus;
  });

  const total = filtered.length;
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const handleToggle = async (lang) => {
    try {
      await toggleLanguage(lang.language_code, lang.is_active);
    } catch {}
  };

  return (
    <div className="page page--active" id="page-languages">
      <div className="filter-bar">
        <div className="search">
          <i className="bx bx-search search__icon" />
          <input
            className="search__input"
            placeholder="Tìm theo tên, mã ngôn ngữ..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
        <div className="filter-bar__actions">
          <select
            className="filter-select"
            value={filterStatus}
            onChange={(e) => {
              setFilterStatus(e.target.value);
              setPage(1);
            }}
          >
            <option value="">Tất cả trạng thái</option>
            <option value="active">Đang hoạt động</option>
            <option value="inactive">Đã tắt</option>
          </select>
          <button
            className="btn btn--primary"
            onClick={() => setShowForm(true)}
          >
            <i className="bx bx-plus" /> Thêm ngôn ngữ
          </button>
        </div>
      </div>

      {showForm && (
        <AddLanguageForm
          onSubmit={async (payload) => {
            await createLanguage(payload);
            setShowForm(false);
          }}
          onCancel={() => setShowForm(false)}
        />
      )}

      {error && <p className="page-error">{error}</p>}

      <div className="data-table">
        <table>
          <colgroup>
            <col />
            <col />
            <col />
            <col />
          </colgroup>
          <thead>
            <tr>
              <th>Mã</th>
              <th>Ngôn ngữ</th>
              <th>Trạng thái</th>
              <th>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} className="data-table__empty">
                  Đang tải...
                </td>
              </tr>
            ) : paginated.length === 0 ? (
              <tr>
                <td colSpan={4} className="data-table__empty">
                  Không có dữ liệu
                </td>
              </tr>
            ) : (
              paginated.map((lang) => (
                <tr key={lang.language_code}>
                  <td>
                    <span className="lang-code">{lang.language_code}</span>
                  </td>
                  <td>
                    <span className="lang-name">{lang.language_name}</span>
                  </td>
                  <td>
                    <Badge variant={lang.is_active ? "active" : "inactive"} dot>
                      {lang.is_active ? "Hoạt động" : "Đã tắt"}
                    </Badge>
                  </td>
                  <td>
                    {lang.is_active ? (
                      <button
                        className="table-action table-action--lock"
                        onClick={() => handleToggle(lang)}
                      >
                        Tắt
                      </button>
                    ) : (
                      <button
                        className="table-action table-action--unlock"
                        onClick={() => handleToggle(lang)}
                      >
                        Bật
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        <Pagination
          current={page}
          total={total}
          limit={PAGE_SIZE}
          onChange={(p) => setPage(p)}
        />
      </div>
    </div>
  );
}
