import { useState, useEffect, createContext, useContext, useCallback } from "react";

// ─── CONFIG ──────────────────────────────────────────────────────────────────
const API_BASE = "http://localhost:8000";

// ─── TEMA DE CORES (paleta da loja de cortinas) ───────────────────────────────
const C = {
  lavender:  "#DCDAE7",  // fundo suave
  sage:      "#90BC8C",  // ação principal / botões
  cream:     "#F5F5DC",  // superfícies / cards
  burgundy:  "#5A2328",  // header / ênfase
  ink:       "#090302",  // texto principal
  sageLight: "#c6ddc4",  // hover botão
  sageDark:  "#6a9c67",  // botão pressionado
  burLight:  "#7a3340",  // hover header
  surface:   "#fafaf5",  // inputs
  border:    "#d6d0c4",
  muted:     "#7a7060",
};

// ─── API HELPER ───────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}, token = null) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Erro ${res.status}`);
  return data;
}

// ─── AUTH CONTEXT ─────────────────────────────────────────────────────────────
const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [currentUser, setCurrentUser] = useState(null);

  const login = useCallback(async (email, password) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    const res = await fetch(`${API_BASE}/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Erro ao fazer login");
    localStorage.setItem("token", data.access_token);
    setToken(data.access_token);
    return data.access_token;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setCurrentUser(null);
  }, []);

  useEffect(() => {
    if (!token) return;
    apiFetch("/me", {}, token)
      .then(setCurrentUser)
      .catch(() => logout());
  }, [token, logout]);

  return (
    <AuthContext.Provider value={{ token, currentUser, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

const useAuth = () => useContext(AuthContext);

// ─── COMPONENTS ───────────────────────────────────────────────────────────────

function Notification({ msg, type, onClose }) {
  if (!msg) return null;
  const map = {
    success: { bg: C.sage, text: "#fff" },
    error:   { bg: C.burgundy, text: "#fff" },
    info:    { bg: C.lavender, text: C.ink },
  };
  const s = map[type] || map.info;
  return (
    <div style={{
      position: "fixed", top: 20, right: 20, zIndex: 9999,
      background: s.bg, color: s.text,
      padding: "12px 20px", borderRadius: 8,
      display: "flex", alignItems: "center", gap: 12, maxWidth: 360,
      fontSize: 14, fontWeight: 500,
    }}>
      <span style={{ flex: 1 }}>{msg}</span>
      <button onClick={onClose} style={{
        background: "none", border: "none", color: s.text,
        cursor: "pointer", fontSize: 18, lineHeight: 1, padding: 0,
      }}>×</button>
    </div>
  );
}

function Input({ label, error, ...props }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      {label && (
        <label style={{ fontSize: 13, fontWeight: 500, color: C.ink, letterSpacing: "0.02em" }}>
          {label}
        </label>
      )}
      <input
        {...props}
        style={{
          padding: "9px 13px", borderRadius: 6, fontSize: 14,
          border: `1.5px solid ${error ? C.burgundy : C.border}`,
          background: C.surface, color: C.ink, outline: "none",
          transition: "border 0.15s",
          ...props.style,
        }}
        onFocus={e => e.target.style.borderColor = C.sage}
        onBlur={e => e.target.style.borderColor = error ? C.burgundy : C.border}
      />
      {error && <span style={{ fontSize: 12, color: C.burgundy }}>{error}</span>}
    </div>
  );
}

function Button({ children, variant = "primary", loading, ...props }) {
  const variants = {
    primary: { background: C.sage, color: "#fff", border: "none" },
    danger:  { background: C.burgundy, color: "#fff", border: "none" },
    ghost:   { background: "transparent", color: C.burgundy, border: `1.5px solid ${C.burgundy}` },
    subtle:  { background: C.lavender, color: C.ink, border: "none" },
  };
  const v = variants[variant] || variants.primary;
  return (
    <button
      {...props}
      disabled={loading || props.disabled}
      style={{
        padding: "9px 18px", borderRadius: 6, fontSize: 14, fontWeight: 600,
        cursor: loading ? "wait" : "pointer",
        display: "inline-flex", alignItems: "center", gap: 6,
        opacity: loading ? 0.7 : 1, transition: "background 0.15s, opacity 0.15s",
        letterSpacing: "0.01em",
        ...v,
        ...props.style,
      }}
      onMouseEnter={e => {
        if (!loading) e.currentTarget.style.background =
          variant === "primary" ? C.sageDark :
          variant === "danger"  ? C.burLight :
          variant === "ghost"   ? "#f5eaeb" : C.sageLight;
      }}
      onMouseLeave={e => {
        e.currentTarget.style.background = v.background;
      }}
    >
      {loading ? "Aguarde..." : children}
    </button>
  );
}

function Card({ title, children, action }) {
  return (
    <div style={{
      background: C.cream, borderRadius: 10,
      border: `1px solid ${C.border}`, padding: 24,
    }}>
      {(title || action) && (
        <div style={{
          display: "flex", justifyContent: "space-between",
          alignItems: "center", marginBottom: 20,
          paddingBottom: 14, borderBottom: `1px solid ${C.border}`,
        }}>
          {title && (
            <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: C.burgundy, letterSpacing: "0.02em" }}>
              {title}
            </h3>
          )}
          {action}
        </div>
      )}
      {children}
    </div>
  );
}

// Decoração de cortina SVG pequena para topo do login
function CurtainDeco() {
  return (
    <svg width="320" height="32" viewBox="0 0 320 32" style={{ display: "block", margin: "0 auto -2px" }}>
      {[0,1,2,3,4,5,6,7].map(i => (
        <path
          key={i}
          d={`M${i*40+20},0 Q${i*40+10},20 ${i*40+20},32 Q${i*40+30},20 ${i*40+40},0`}
          fill={i % 2 === 0 ? C.burgundy : C.sage}
          opacity="0.85"
        />
      ))}
    </svg>
  );
}

// ─── LOGIN ────────────────────────────────────────────────────────────────────
function LoginPage({ onRegister }) {
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setError("");
    setLoading(true);
    try {
      await login(form.email, form.password);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: C.lavender, padding: "20px",
    }}>
      <div style={{ width: "100%", maxWidth: "420px" }}>
        <div style={{
          background: C.burgundy, borderRadius: "12px 12px 0 0",
          padding: "22px 28px 18px", textAlign: "center",
        }}>
          <CurtainDeco />
          <h1 style={{ margin: "10px 0 4px", fontSize: 22, fontWeight: 800, color: C.cream, letterSpacing: "0.04em" }}>
            LeCortinas
          </h1>
          <p style={{ margin: 0, fontSize: 13, color: C.sageLight }}>Gestão da sua loja</p>
        </div>

        <div style={{
          background: C.cream, borderRadius: "0 0 12px 12px",
          border: `1px solid ${C.border}`, borderTop: "none",
          padding: "28px 28px 24px",
        }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <Input
              label="E-mail"
              type="email"
              placeholder="seu@email.com"
              value={form.email}
              onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
            />
            <Input
              label="Senha"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              onKeyDown={e => e.key === "Enter" && handleSubmit()}
            />
            {error && (
              <div style={{
                background: "#fdf2f2", border: `1px solid ${C.burgundy}`,
                borderRadius: 6, padding: "10px 12px", color: C.burgundy, fontSize: 13,
              }}>
                {error}
              </div>
            )}
            <Button onClick={handleSubmit} loading={loading} style={{ width: "100%", justifyContent: "center", marginTop: 4 }}>
              Entrar
            </Button>
            <p style={{ textAlign: "center", fontSize: 13, color: C.muted, margin: 0 }}>
              Sem conta?{" "}
              <span onClick={onRegister} style={{ color: C.burgundy, cursor: "pointer", fontWeight: 600 }}>
                Cadastre-se
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── REGISTER ─────────────────────────────────────────────────────────────────
function RegisterPage({ onBack, onNotify }) {
  const [form, setForm] = useState({ name: "", age: "", email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const e = {};
    if (!form.name.trim()) e.name = "Nome obrigatório";
    if (!form.age || parseInt(form.age) < 18) e.age = "Deve ter ao menos 18 anos";
    if (!form.email.includes("@")) e.email = "E-mail inválido";
    if (!form.password || form.password.length < 4) e.password = "Senha muito curta";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      await apiFetch("/users/", {
        method: "POST",
        body: JSON.stringify({ ...form, age: parseInt(form.age) }),
      });
      onNotify("Conta criada! Faça login.", "success");
      onBack();
    } catch (e) {
      onNotify(e.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const f = (key) => ({
    value: form[key], error: errors[key],
    onChange: e => setForm(p => ({ ...p, [key]: e.target.value })),
  });

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: C.lavender, padding: "20px",
    }}>
      <div style={{ width: "100%", maxWidth: 420 }}>
        <div style={{
          background: C.burgundy, borderRadius: "12px 12px 0 0",
          padding: "22px 28px 18px", textAlign: "center",
        }}>
          <CurtainDeco />
          <h1 style={{ margin: "10px 0 4px", fontSize: 20, fontWeight: 800, color: C.cream }}>
            Criar conta
          </h1>
          <p style={{ margin: 0, fontSize: 13, color: C.sageLight }}>LeCortinas</p>
        </div>
        <div style={{
          background: C.cream, borderRadius: "0 0 12px 12px",
          border: `1px solid ${C.border}`, borderTop: "none",
          padding: "28px 28px 24px",
        }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <Input label="Nome completo" placeholder="Seu nome" {...f("name")} />
            <Input label="Idade" type="number" placeholder="25" {...f("age")} />
            <Input label="E-mail" type="email" placeholder="seu@email.com" {...f("email")} />
            <Input label="Senha" type="password" placeholder="••••••••" {...f("password")} />
            <Button onClick={handleSubmit} loading={loading} style={{ width: "100%", justifyContent: "center", marginTop: 4 }}>
              Criar Conta
            </Button>
            <p style={{ textAlign: "center", fontSize: 13, color: C.muted, margin: 0 }}>
              Já tem conta?{" "}
              <span onClick={onBack} style={{ color: C.burgundy, cursor: "pointer", fontWeight: 600 }}>
                Entrar
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── CUSTOMERS ────────────────────────────────────────────────────────────────
function CustomersSection({ token, onNotify }) {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", age: "", address: "", password: "" });
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiFetch("/customers/", {}, token);
      setCustomers(data.customers || []);
    } catch (e) {
      onNotify(e.message, "error");
    } finally {
      setLoading(false);
    }
  }, [token, onNotify]);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async () => {
    setSaving(true);
    try {
      await apiFetch("/customers/", {
        method: "POST",
        body: JSON.stringify({ ...form, age: form.age ? parseInt(form.age) : null }),
      }, token);
      onNotify("Cliente cadastrado!", "success");
      setShowForm(false);
      setForm({ name: "", email: "", age: "", address: "", password: "" });
      load();
    } catch (e) {
      onNotify(e.message, "error");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Remover este cliente?")) return;
    try {
      await apiFetch(`/customers/${id}`, { method: "DELETE" }, token);
      onNotify("Cliente removido.", "info");
      load();
    } catch (e) {
      onNotify(e.message, "error");
    }
  };

  return (
    <Card
      title="Clientes"
      action={
        <Button
          variant={showForm ? "subtle" : "primary"}
          onClick={() => setShowForm(s => !s)}
        >
          {showForm ? "Cancelar" : "+ Novo cliente"}
        </Button>
      }
    >
      {showForm && (
        <div style={{
          display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12,
          marginBottom: 20, padding: 16,
          background: C.lavender, borderRadius: 8,
          border: `1px solid ${C.border}`,
        }}>
          {[
            { key: "name", label: "Nome *", placeholder: "Nome do cliente" },
            { key: "email", label: "E-mail *", type: "email", placeholder: "email@..." },
            { key: "age", label: "Idade", type: "number", placeholder: "30" },
            { key: "address", label: "Endereço", placeholder: "Rua, número..." },
            { key: "password", label: "Senha", type: "password", placeholder: "••••" },
          ].map(({ key, label, ...rest }) => (
            <Input
              key={key} label={label} {...rest}
              value={form[key]}
              onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))}
            />
          ))}
          <div style={{ display: "flex", alignItems: "flex-end" }}>
            <Button onClick={handleCreate} loading={saving} style={{ width: "100%", justifyContent: "center" }}>
              Salvar
            </Button>
          </div>
        </div>
      )}

      {loading ? (
        <p style={{ color: C.muted, textAlign: "center", margin: "24px 0" }}>Carregando clientes...</p>
      ) : customers.length === 0 ? (
        <div style={{ textAlign: "center", padding: "28px 0", color: C.muted }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>👤</div>
          <p style={{ margin: 0, fontSize: 14 }}>Nenhum cliente cadastrado ainda.</p>
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead>
            <tr style={{ background: C.lavender }}>
              {["Nome", "E-mail", "Idade", "Endereço", ""].map((h, i) => (
                <th key={i} style={{
                  padding: "9px 12px", textAlign: "left",
                  color: C.muted, fontWeight: 600, fontSize: 12,
                  textTransform: "uppercase", letterSpacing: "0.05em",
                  borderBottom: `1.5px solid ${C.border}`,
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {customers.map((c, idx) => (
              <tr
                key={c.id}
                style={{ background: idx % 2 === 0 ? C.cream : "#f0efe8", transition: "background 0.1s" }}
                onMouseEnter={e => e.currentTarget.style.background = C.lavender}
                onMouseLeave={e => e.currentTarget.style.background = idx % 2 === 0 ? C.cream : "#f0efe8"}
              >
                <td style={{ padding: "11px 12px", fontWeight: 600, color: C.ink }}>{c.name}</td>
                <td style={{ padding: "11px 12px", color: C.muted }}>{c.email || "—"}</td>
                <td style={{ padding: "11px 12px", color: C.ink }}>{c.age || "—"}</td>
                <td style={{ padding: "11px 12px", color: C.muted }}>{c.address || "—"}</td>
                <td style={{ padding: "11px 12px", textAlign: "right" }}>
                  <Button variant="ghost" onClick={() => handleDelete(c.id)} style={{ padding: "5px 12px", fontSize: 12 }}>
                    Remover
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Card>
  );
}

// ─── ORDERS ───────────────────────────────────────────────────────────────────
function OrdersSection({ token, onNotify }) {
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ customer_id: "", description: "" });
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [o, c] = await Promise.all([
        apiFetch("/orders/", {}, token),
        apiFetch("/customers/", {}, token),
      ]);
      setOrders(o.orders || []);
      setCustomers(c.customers || []);
    } catch (e) {
      onNotify(e.message, "error");
    } finally {
      setLoading(false);
    }
  }, [token, onNotify]);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async () => {
    if (!form.customer_id || !form.description) return onNotify("Preencha todos os campos", "error");
    setSaving(true);
    try {
      await apiFetch("/orders/", { method: "POST", body: JSON.stringify(form) }, token);
      onNotify("Pedido criado!", "success");
      setShowForm(false);
      setForm({ customer_id: "", description: "" });
      load();
    } catch (e) {
      onNotify(e.message, "error");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Remover este pedido?")) return;
    try {
      await apiFetch(`/orders/${id}`, { method: "DELETE" }, token);
      onNotify("Pedido removido.", "info");
      load();
    } catch (e) {
      onNotify(e.message, "error");
    }
  };

  const getCustomerName = (id) => customers.find(c => c.id === id)?.name || "—";

  return (
    <Card
      title="Pedidos"
      action={
        <Button
          variant={showForm ? "subtle" : "primary"}
          onClick={() => setShowForm(s => !s)}
        >
          {showForm ? "Cancelar" : "+ Novo pedido"}
        </Button>
      }
    >
      {showForm && (
        <div style={{
          display: "flex", flexDirection: "column", gap: 12,
          marginBottom: 20, padding: 16,
          background: C.lavender, borderRadius: 8, border: `1px solid ${C.border}`,
        }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <label style={{ fontSize: 13, fontWeight: 500, color: C.ink }}>Cliente *</label>
            <select
              value={form.customer_id}
              onChange={e => setForm(p => ({ ...p, customer_id: e.target.value }))}
              style={{
                padding: "9px 13px", borderRadius: 6, fontSize: 14,
                border: `1.5px solid ${C.border}`, background: C.surface, color: C.ink,
              }}
            >
              <option value="">Selecione um cliente</option>
              {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <Input
            label="Descrição do pedido *"
            placeholder="Ex: Cortina blackout para sala, 2,20m × 1,80m, cor creme..."
            value={form.description}
            onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
          />
          <Button onClick={handleCreate} loading={saving} style={{ alignSelf: "flex-start" }}>
            Registrar pedido
          </Button>
        </div>
      )}

      {loading ? (
        <p style={{ color: C.muted, textAlign: "center", margin: "24px 0" }}>Carregando pedidos...</p>
      ) : orders.length === 0 ? (
        <div style={{ textAlign: "center", padding: "28px 0", color: C.muted }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📋</div>
          <p style={{ margin: 0, fontSize: 14 }}>Nenhum pedido registrado ainda.</p>
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead>
            <tr style={{ background: C.lavender }}>
              {["Cliente", "Descrição do pedido", ""].map((h, i) => (
                <th key={i} style={{
                  padding: "9px 12px", textAlign: "left",
                  color: C.muted, fontWeight: 600, fontSize: 12,
                  textTransform: "uppercase", letterSpacing: "0.05em",
                  borderBottom: `1.5px solid ${C.border}`,
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {orders.map((o, idx) => (
              <tr
                key={o.id}
                style={{ background: idx % 2 === 0 ? C.cream : "#f0efe8" }}
                onMouseEnter={e => e.currentTarget.style.background = C.lavender}
                onMouseLeave={e => e.currentTarget.style.background = idx % 2 === 0 ? C.cream : "#f0efe8"}
              >
                <td style={{ padding: "11px 12px", fontWeight: 600, color: C.ink, whiteSpace: "nowrap" }}>
                  {getCustomerName(o.customer_id)}
                </td>
                <td style={{ padding: "11px 12px", color: C.muted }}>{o.description}</td>
                <td style={{ padding: "11px 12px", textAlign: "right" }}>
                  <Button variant="ghost" onClick={() => handleDelete(o.id)} style={{ padding: "5px 12px", fontSize: 12 }}>
                    Remover
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Card>
  );
}

// ─── DASHBOARD ────────────────────────────────────────────────────────────────
function Dashboard() {
  const { currentUser, logout, token } = useAuth();
  const [tab, setTab] = useState("customers");
  const [notif, setNotif] = useState(null);

  const notify = useCallback((msg, type = "info") => {
    setNotif({ msg, type });
    setTimeout(() => setNotif(null), 4000);
  }, []);

  const tabs = [
    { id: "customers", label: "Clientes" },
    { id: "orders",    label: "Pedidos" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: C.lavender }}>
      <Notification msg={notif?.msg} type={notif?.type} onClose={() => setNotif(null)} />

      {/* Header */}
      <header style={{
        background: C.burgundy, padding: "0 28px", height: 58,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 100,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 22 }}>🪟</span>
          <span style={{ fontWeight: 800, fontSize: 17, color: C.cream, letterSpacing: "0.04em" }}>
            LeCortinas
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span style={{ fontSize: 13, color: C.sageLight }}>
            {currentUser?.email}
          </span>
          <Button variant="ghost" onClick={logout} style={{
            padding: "6px 14px", fontSize: 13,
            color: C.cream, border: `1px solid ${C.sageLight}`,
          }}>
            Sair
          </Button>
        </div>
      </header>

      {/* Tabs */}
      <div style={{
        background: C.ink, padding: "0 28px", display: "flex", gap: 2,
      }}>
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            style={{
              padding: "13px 20px", border: "none",
              background: tab === t.id ? C.burgundy : "transparent",
              fontSize: 14, fontWeight: tab === t.id ? 700 : 400,
              color: tab === t.id ? C.cream : C.muted,
              cursor: "pointer", transition: "all 0.15s",
              borderBottom: tab === t.id ? `3px solid ${C.sage}` : "3px solid transparent",
              letterSpacing: "0.02em",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <main style={{ maxWidth: 900, margin: "0 auto", padding: "28px 20px" }}>
        {tab === "customers" && <CustomersSection token={token} onNotify={notify} />}
        {tab === "orders"    && <OrdersSection    token={token} onNotify={notify} />}
      </main>
    </div>
  );
}

// ─── APP ──────────────────────────────────────────────────────────────────────
function AppContent() {
  const { token } = useAuth();
  const [page, setPage] = useState("login");
  const [notif, setNotif] = useState(null);

  const notify = useCallback((msg, type = "info") => {
    setNotif({ msg, type });
    setTimeout(() => setNotif(null), 4000);
  }, []);

  if (token) return <Dashboard />;

  return (
    <>
      <Notification msg={notif?.msg} type={notif?.type} onClose={() => setNotif(null)} />
      {page === "login"    && <LoginPage    onRegister={() => setPage("register")} />}
      {page === "register" && <RegisterPage onBack={() => setPage("login")} onNotify={notify} />}
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}