import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  Calendar,
  MapPin,
  LogOut,
  Plus,
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  Moon,
  Sun,
  Loader2,
  UserPlus,
  ShieldCheck,
  Trash2,
  ScanLine,
  AlertCircle,
  Mail,
  Lock,
  User as UserIcon,
  Users,
  Ticket as TicketIcon,
  Search,
  Link2,
  CalendarPlus,
  Info,
} from "lucide-react";

import { useTheme } from "./components/theme-provider";

// ---------------------------------------------------------------------------
// Configuração da URL da API do FastAPI
// ---------------------------------------------------------------------------
import axiosInstance from "./api";
/**
 * Utilitário centralizado para requisições HTTP da API
 */
async function apiRequest(path, { method = "GET", token, body, form } = {}) {
  const config = {
    method,
    url: path,
    headers: {},
  };

  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }

  if (form) {
    config.data = new URLSearchParams(body).toString();
    config.headers["Content-Type"] = "application/x-www-form-urlencoded";
  } else if (body !== undefined) {
    config.data = body;
    config.headers["Content-Type"] = "application/json";
  }

  try {
    const response = await axiosInstance(config);
    return response.data;
  } catch (error) {
    if (error.response) {
      const detail = error.response.data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((d) => d.msg).join(", ")
        : detail || `Erro ${error.response.status}`;
      
      const err = new Error(message);
      err.status = error.response.status;
      throw err;
    } else {
      // Acessa a URL configurada no axios de forma segura para a mensagem de erro
      const currentBaseUrl = axiosInstance.defaults.baseURL || "o servidor";
      const err = new Error(`Não foi possível conectar. Verifique se a API está rodando em ${currentBaseUrl}`);
      err.status = 0;
      throw err;
    }
  }
}

function extractEventId(input) {
  const trimmed = input.trim();
  const match = trimmed.match(
    /[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/
  );
  return match ? match[0] : trimmed;
}

function formatDateTime(value) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString("pt-BR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return value;
  }
}

function initials(name = "") {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join("") || "?";
}

// ---------------------------------------------------------------------------
// Componentes de Interface (Baseados nas classes utilitárias do index.css)
// ---------------------------------------------------------------------------

function Button({ variant = "primary", size = "md", className = "", children, ...props }) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:pointer-events-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring select-none cursor-pointer";
  const variants = {
    primary: "bg-primary text-primary-foreground hover:opacity-90",
    secondary: "bg-secondary text-secondary-foreground hover:bg-muted",
    outline: "border border-border bg-transparent hover:bg-accent hover:text-accent-foreground",
    ghost: "bg-transparent hover:bg-accent hover:text-accent-foreground",
    destructive: "bg-destructive text-white hover:opacity-90",
  };
  const sizes = {
    sm: "h-8 px-3 text-xs",
    md: "h-10 px-4 text-sm",
    lg: "h-11 px-5 text-sm",
    icon: "h-9 w-9",
  };
  return (
    <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...props}>
      {children}
    </button>
  );
}

function Input({ className = "", ...props }) {
  return (
    <input
      {...props}
      className={`h-10 w-full rounded-lg border border-input bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${className}`}
    />
  );
}

function Textarea({ className = "", ...props }) {
  return (
    <textarea
      {...props}
      className={`w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${className}`}
    />
  );
}

function Label({ children, ...props }) {
  return (
    <label {...props} className="mb-1.5 block text-sm font-medium text-foreground">
      {children}
    </label>
  );
}

function Card({ className = "", children, ...props }) {
  return (
    <div
      {...props}
      className={`rounded-2xl border border-border bg-card text-card-foreground shadow-sm ${className}`}
    >
      {children}
    </div>
  );
}

function Badge({ tone = "default", className = "", children }) {
  const tones = {
    default: "bg-secondary text-secondary-foreground",
    admin: "bg-primary text-primary-foreground",
    staff: "bg-foreground/10 text-foreground",
    success: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
    warn: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
    danger: "bg-destructive/10 text-destructive",
  };
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${tones[tone]} ${className}`}
    >
      {children}
    </span>
  );
}

function Spinner({ className = "h-4 w-4" }) {
  return <Loader2 className={`animate-spin ${className}`} />;
}

function Alert({ tone = "error", children }) {
  const tones = {
    error: "border-destructive/30 bg-destructive/10 text-destructive",
    info: "border-primary/30 bg-primary/10 text-primary",
    success: "border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
  };
  const Icon = tone === "success" ? CheckCircle2 : tone === "info" ? Info : AlertCircle;
  return (
    <div className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-sm ${tones[tone]}`}>
      <Icon className="mt-0.5 h-4 w-4 shrink-0" />
      <span>{children}</span>
    </div>
  );
}

function EmptyState({ icon: Icon = Info, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-border px-6 py-14 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <p className="font-medium text-foreground">{title}</p>
        {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      </div>
      {action}
    </div>
  );
}

function Modal({ open, onClose, title, children }) {
  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm transition-opacity"
      onClick={onClose}
    >
      <Card
        className="w-full max-w-md p-6 animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-5 flex items-center justify-between">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground cursor-pointer"
          >
            <XCircle className="h-5 w-5" />
          </button>
        </div>
        {children}
      </Card>
    </div>
  );
}

function TicketStub({ eventName, holderName, code, checkedIn }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Falha silenciosa se clipboard não estiver disponível
    }
  }

  return (
    <div className="relative flex w-full overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary to-primary/80 text-primary-foreground shadow-md">
      <div className="flex-1 p-5">
        <div className="flex items-center gap-2 text-xs uppercase tracking-widest text-primary-foreground/70">
          <TicketIcon className="h-3.5 w-3.5" />
          Ingresso
        </div>
        <p className="mt-2 text-lg font-semibold leading-tight">{eventName}</p>
        <p className="text-sm text-primary-foreground/85 mt-0.5">{holderName}</p>
        <div className="mt-4">
          {checkedIn ? (
            <Badge className="bg-white/20 text-primary-foreground">
              <CheckCircle2 className="h-3 w-3" /> Presença Confirmada
            </Badge>
          ) : (
            <Badge className="bg-white/10 text-primary-foreground border border-white/20">
              Aguardando Check-in
            </Badge>
          )}
        </div>
      </div>
      <div className="relative flex w-32 shrink-0 flex-col items-center justify-center gap-2 border-l border-dashed border-primary-foreground/30 px-3 py-4 bg-black/5">
        <div className="absolute -top-2 -left-2 h-4 w-4 rounded-full bg-background" />
        <div className="absolute -bottom-2 -left-2 h-4 w-4 rounded-full bg-background" />
        <p className="break-all text-center font-mono text-[10px] uppercase tracking-wider text-primary-foreground/90">
          {code}
        </p>
        <button
          onClick={handleCopy}
          className="mt-1 inline-flex items-center gap-1 rounded-md bg-white/15 px-2 py-1 text-[11px] font-medium text-primary-foreground transition-colors hover:bg-white/25 cursor-pointer"
        >
          {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
          {copied ? "Copiado" : "Copiar"}
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-telas: Autenticação
// ---------------------------------------------------------------------------

function AuthScreen({ api, onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [registerForm, setRegisterForm] = useState({ name: "", email: "", password: "", age: "" });

  async function handleLogin() {
    setLoading(true);
    setError("");
    try {
      const tokenData = await api("/login", {
        form: true,
        method: "POST",
        body: { username: loginForm.email, password: loginForm.password },
      });
      const me = await api("/me", { token: tokenData.access_token });
      onAuthenticated(tokenData.access_token, me);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister() {
    setLoading(true);
    setError("");
    try {
      const payload = {
        name: registerForm.name,
        email: registerForm.email,
        password: registerForm.password,
      };
      if (registerForm.age) payload.age = Number(registerForm.age);
      await api("/users", { method: "POST", body: payload });
      setNotice("Conta criada com sucesso! Faça login abaixo.");
      setLoginForm({ email: registerForm.email, password: "" });
      setRegisterForm({ name: "", email: "", password: "", age: "" });
      setMode("login");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit() {
    setNotice("");
    if (mode === "login") handleLogin();
    else handleRegister();
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-10">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
            <CalendarPlus className="h-6 w-6" />
          </div>
          <h1 className="text-xl font-semibold text-foreground">Sistema de Eventos</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {mode === "login" ? "Gerencie ou participe de eventos organizados" : "Cadastre-se para começar"}
          </p>
        </div>

        <Card className="p-6 shadow-md bg-card">
          <div className="mb-5 grid grid-cols-2 gap-1 rounded-lg bg-muted p-1">
            <button
              onClick={() => { setMode("login"); setError(""); }}
              className={`rounded-md py-1.5 text-sm font-medium transition-colors cursor-pointer ${
                mode === "login" ? "bg-background text-foreground shadow-sm" : "text-muted-foreground"
              }`}
            >
              Entrar
            </button>
            <button
              onClick={() => { setMode("register"); setError(""); }}
              className={`rounded-md py-1.5 text-sm font-medium transition-colors cursor-pointer ${
                mode === "register" ? "bg-background text-foreground shadow-sm" : "text-muted-foreground"
              }`}
            >
              Cadastrar
            </button>
          </div>

          <div className="space-y-4">
            {mode === "register" && (
              <div>
                <Label htmlFor="name">Nome Completo</Label>
                <div className="relative">
                  <UserIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="name"
                    className="pl-9"
                    placeholder="João da Silva"
                    value={registerForm.name}
                    onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })}
                  />
                </div>
              </div>
            )}

            <div>
              <Label htmlFor="email">E-mail</Label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  className="pl-9"
                  placeholder="exemplo@email.com"
                  value={mode === "login" ? loginForm.email : registerForm.email}
                  onChange={(e) =>
                    mode === "login"
                      ? setLoginForm({ ...loginForm, email: e.target.value })
                      : setRegisterForm({ ...registerForm, email: e.target.value })
                  }
                />
              </div>
            </div>

            <div>
              <Label htmlFor="password">Senha</Label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  className="pl-9"
                  placeholder="••••••••"
                  value={mode === "login" ? loginForm.password : registerForm.password}
                  onChange={(e) =>
                    mode === "login"
                      ? setLoginForm({ ...loginForm, password: e.target.value })
                      : setRegisterForm({ ...registerForm, password: e.target.value })
                  }
                  onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                />
              </div>
            </div>

            {mode === "register" && (
              <div>
                <Label htmlFor="age">Idade (opcional)</Label>
                <Input
                  id="age"
                  type="number"
                  min="0"
                  placeholder="Ex: 25"
                  value={registerForm.age}
                  onChange={(e) => setRegisterForm({ ...registerForm, age: e.target.value })}
                />
              </div>
            )}

            {error && <Alert tone="error">{error}</Alert>}
            {notice && <Alert tone="success">{notice}</Alert>}

            <Button className="w-full mt-2" onClick={handleSubmit} disabled={loading}>
              {loading && <Spinner />}
              {mode === "login" ? "Entrar na conta" : "Criar minha conta"}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-telas: Dashboard Geral
// ---------------------------------------------------------------------------

function Dashboard({ api, events, eventsLoading, eventsError, onRefresh, onOpenEvent }) {
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", date: "", location: "", description: "" });
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");

  const [joinValue, setJoinValue] = useState("");
  const [joinLoading, setJoinLoading] = useState(false);
  const [joinError, setJoinError] = useState("");
  const roleConfig = {
  admin: {
    tone: "admin",
    label: "Administrador",
    },
  staff: {
    tone: "staff",
    label: "Equipe",
    },
  attendee: {
    tone: "attendee",
    label: "Participante",
    },
  };

  async function handleCreate() {
    setCreating(true);
    setCreateError("");
    try {
      if (!form.name || !form.date || !form.location) {
        throw new Error("Por favor, informe no mínimo o nome, a data e o local.");
      }
      const payload = {
        name: form.name,
        date: new Date(form.date).toISOString(),
        location: form.location,
        description: form.description || null,
      };
      await api("/events/", { method: "POST", body: payload });
      setShowCreate(false);
      setForm({ name: "", date: "", location: "", description: "" });
      onRefresh();
    } catch (e) {
      setCreateError(e.message);
    } finally {
      setCreating(false);
    }
  }

  async function handleJoin() {
    setJoinLoading(true);
    setJoinError("");
    try {
      const id = extractEventId(joinValue);
      const event = await api(`/events/${id}`);
      const membership = events.find((e) => e.id === event.id);
      onOpenEvent({ ...event, role: membership ? membership.role : null });
      setJoinValue("");
    } catch (e) {
      setJoinError(e.message);
    } finally {
      setJoinLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Seus Eventos</h1>
          <p className="text-sm text-muted-foreground">
            Abaixo estão os eventos cadastrados em seu nome ou onde você atua na equipe de organização.
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="h-4 w-4" /> Novo Evento
        </Button>
      </div>

      <Card className="mb-8 p-5 bg-card border-border">
        <p className="mb-1 flex items-center gap-2 text-sm font-semibold text-foreground">
          <Link2 className="h-4 w-4 text-primary" /> Acessar Evento por ID
        </p>
        <p className="mb-4 text-xs text-muted-foreground">
          Caso possua o identificador UUID único de um evento externo, busque-o diretamente aqui.
        </p>
        <div className="flex flex-col gap-2 sm:flex-row">
          <Input
            placeholder="Cole o ID do evento (ex: 8b4a2e...)"
            value={joinValue}
            onChange={(e) => setJoinValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && joinValue && handleJoin()}
          />
          <Button variant="outline" onClick={handleJoin} disabled={!joinValue || joinLoading}>
            {joinLoading ? <Spinner /> : <Search className="h-4 w-4" />}
            Buscar
          </Button>
        </div>
        {joinError && (
          <div className="mt-3">
            <Alert tone="error">{joinError}</Alert>
          </div>
        )}
      </Card>

      {eventsError && (
        <div className="mb-4">
          <Alert tone="error">{eventsError}</Alert>
        </div>
      )}

      {eventsLoading ? (
        <div className="flex justify-center py-16">
          <Spinner className="h-7 w-7 text-muted-foreground" />
        </div>
      ) : events.length === 0 ? (
        <EmptyState
          icon={Calendar}
          title="Nenhum evento registrado"
          description="Você ainda não faz parte da organização de nenhum evento no momento."
          action={
            <Button size="sm" onClick={() => setShowCreate(true)}>
              <Plus className="h-4 w-4" /> Criar Primeiro Evento
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {events.map((ev) => (
            <button key={ev.id} onClick={() => onOpenEvent(ev)} className="w-full text-left group cursor-pointer">
              <Card className="p-5 transition-all duration-200 hover:border-primary/50 hover:shadow-sm">
                <div className="mb-3 flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">{ev.name}</h3>
                  <Badge tone={roleConfig[ev.role].tone}>
                    {roleConfig[ev.role].label}
                  </Badge>
                </div>
                <div className="space-y-1.5 text-xs text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-3.5 w-3.5 text-muted-foreground" /> {formatDateTime(ev.date)}
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="h-3.5 w-3.5 text-muted-foreground" /> {ev.location}
                  </div>
                </div>
                {ev.description && (
                  <p className="mt-3 line-clamp-2 text-xs text-muted-foreground/90 border-t border-border/40 pt-2.5">
                    {ev.description}
                  </p>
                )}
              </Card>
            </button>
          ))}
        </div>
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Criar Novo Evento">
        <div className="space-y-4">
          <div>
            <Label htmlFor="ev-name">Nome do Evento *</Label>
            <Input
              id="ev-name"
              placeholder="Ex: Workshop de React e Python"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="ev-date">Data e Horário *</Label>
            <Input
              id="ev-date"
              type="datetime-local"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="ev-location">Localização / Link *</Label>
            <Input
              id="ev-location"
              placeholder="Ex: Auditório Principal ou URL do Zoom"
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="ev-description">Descrição Completa</Label>
            <Textarea
              id="ev-description"
              rows={3}
              placeholder="Detalhes sobre a programação, palestrantes, etc..."
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
          {createError && <Alert tone="error">{createError}</Alert>}
          <Button className="w-full mt-2" onClick={handleCreate} disabled={creating}>
            {creating && <Spinner />}
            Confirmar e Registrar Evento
          </Button>
        </div>
      </Modal>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-telas: Detalhes e Gerenciamento do Evento
// ---------------------------------------------------------------------------

function EventDetail({ api, event, currentUser, onBack, onDeleted }) {
  const isAdmin = event.role === "admin";
  const isStaffOrAdmin = event.role === "admin" || event.role === "staff";

  const [tab, setTab] = useState("overview");

  const [tickets, setTickets] = useState([]);
  const [ticketsLoading, setTicketsLoading] = useState(false);
  const [ticketsError, setTicketsError] = useState("");
  const [usersCache, setUsersCache] = useState({});

  const [myTicket, setMyTicket] = useState(null);
  const [ticketActionLoading, setTicketActionLoading] = useState(false);
  const [ticketActionError, setTicketActionError] = useState("");

  const [organizers, setOrganizers] = useState(null);
  const [organizersLoading, setOrganizersLoading] = useState(false);
  const [organizersError, setOrganizersError] = useState("");

  const [staffEmail, setStaffEmail] = useState("");
  const [staffLoading, setStaffLoading] = useState(false);
  const [staffMsg, setStaffMsg] = useState(null);

  const [checkinCode, setCheckinCode] = useState("");
  const [checkinLoading, setCheckinLoading] = useState(false);
  const [checkinResult, setCheckinResult] = useState(null);

  const [checkinLogs, setCheckinLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(false);

  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);

  const loadTickets = useCallback(async () => {
    setTicketsLoading(true);
    setTicketsError("");
    try {
      const data = await api(`/attendees/participants/${event.id}`);
      setTickets(data.tickets);
      const mine = data.tickets.find((t) => t.attendee_id === currentUser.id);
      if (mine) setMyTicket(mine);
    } catch (e) {
      setTicketsError(e.message);
    } finally {
      setTicketsLoading(false);
    }
  }, [api, event.id, currentUser.id]);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  // Busca e cacheia informações de usuários em segundo plano baseando-se no attendee_id
  useEffect(() => {
    const missing = [...new Set(tickets.map((t) => t.attendee_id))].filter(
      (id) => !usersCache[id]
    );
    if (missing.length === 0) return;
    let isMounted = true;
    Promise.allSettled(missing.map((id) => api(`/users/${id}`))).then((results) => {
      if (!isMounted) return;
      setUsersCache((prev) => {
        const next = { ...prev };
        results.forEach((r, idx) => {
          if (r.status === "fulfilled") next[missing[idx]] = r.value;
        });
        return next;
      });
    });
    return () => { isMounted = false; };
  }, [tickets, usersCache, api]);

  const loadCheckInLogs = useCallback(async () => {
    if (!event?.id || !myTicket?.ticket_code) return;
    setLogsLoading(true);
    try {
    // Rota que busca os logs de check-in deste evento
    // (Ajuste o endpoint de acordo com a rota do seu backend, ex: /events/{id}/check-in-logs)
      const data = await api(`/events/${event.id}/check-in-logs?ticket_code=${encodeURIComponent(myTicket.ticket_code)}`);
      setCheckinLogs(data.logs ?? []);
      } catch (e) {
      console.error("Erro ao carregar logs de check-in:", e.message);
      } finally {
      setLogsLoading(false);
    }
  }, [api, event.id, myTicket]);

  // Carrega os logs ao selecionar a aba de check-in
  useEffect(() => {
    if (tab === "checkin" && isStaffOrAdmin) {
      loadCheckInLogs();
    }
  }, [tab, isStaffOrAdmin, loadCheckInLogs]);

  // Modifique a função handleCheckIn para recarregar os logs logo após uma validação bem-sucedida
  async function handleCheckIn() {
    if (!checkinCode) return;
    setCheckinLoading(true);
    setCheckinResult(null);
    try {
      const data = await api(`/events/${event.id}/check-in/${checkinCode.trim()}`, { method: "POST" });
      setCheckinResult({ tone: "success", text: data.message });
      setCheckinCode("");
    
    // Atualiza os dados na tela
      loadTickets();
      loadCheckInLogs(); 
    } catch (e) {
      setCheckinResult({ tone: "error", text: e.message });
    } finally {
      setCheckinLoading(false);
    }
  }

  async function handleGetTicket() {
    setTicketActionLoading(true);
    setTicketActionError("");
    try {
      const data = await api(`/attendees/tickets?event_id=${encodeURIComponent(event.id)}`, { method: "POST" });
      setMyTicket(data.ticket);
      setTickets((prev) => [...prev, data.ticket]);
    } catch (e) {
      setTicketActionError(e.message);
    } finally {
      setTicketActionLoading(false);
    }
  }

  async function loadOrganizers() {
    if (!myTicket) return;
    setOrganizersLoading(true);
    setOrganizersError("");
    try {
      const data = await api(
        `/attendees/organizers/${event.id}?ticket_code=${encodeURIComponent(myTicket.ticket_code)}`
      );
      const organizersList = data.users.filter((t) => t.role === "admin" || t.role === "staff");
      setOrganizers(organizersList);
    } catch (e) {
      setOrganizersError(e.message);
    } finally {
      setOrganizersLoading(false);
    }
  }

  useEffect(() => {
    if (tab === "team" && isStaffOrAdmin && myTicket && organizers === null) {
      loadOrganizers();
    }
  }, [tab, myTicket, organizers, isStaffOrAdmin]);

  async function handleAddStaff() {
    if (!myTicket) return;
    setStaffLoading(true);
    setStaffMsg(null);
    try {
      const targetUser = await api(`/users/by-email/${encodeURIComponent(staffEmail)}`);
      await api(
        `/events/${event.id}/addstaff/${targetUser.id}?ticket_code=${encodeURIComponent(
          myTicket.ticket_code
        )}`,
        { method: "POST" }
      );
      setStaffMsg({ tone: "success", text: `${targetUser.name} adicionado à equipe organizacional!` });
      setStaffEmail("");
      setOrganizers(null);
      loadOrganizers();
    } catch (e) {
      setStaffMsg({ tone: "error", text: e.message });
    } finally {
      setStaffLoading(false);
    }
  }

  async function handleCheckIn() {
    if (!checkinCode) return;
    setCheckinLoading(true);
    setCheckinResult(null);
    try {
      const data = await api(`/events/${event.id}/check-in/${checkinCode.trim()}`, { method: "POST" });
      setCheckinResult({ tone: "success", text: data.message });
      setCheckinCode("");
      loadTickets();
    } catch (e) {
      setCheckinResult({ tone: "error", text: e.message });
    } finally {
      setCheckinLoading(false);
    }
  }



  async function handleDeleteEvent() {
    if (!myTicket) return;
    setDeleteLoading(true);
    setDeleteError("");
    try {
      await api(`/events/${event.id}?ticket_code=${encodeURIComponent(myTicket.ticket_code)}`, {
        method: "DELETE",
      });
      onDeleted(event.id);
    } catch (e) {
      setDeleteError(e.message);
    } finally {
      setDeleteLoading(false);
    }
  }


  const tabList = useMemo(() => {
    const items = [
      { id: "overview", label: "Visão Geral", icon: Info },
      { id: "ticket", label: "Meu Ingresso", icon: TicketIcon }
    ];
    if (isStaffOrAdmin) {
      items.push({ id: "participants", label: "Inscritos", icon: Users });
      items.push({ id: "team", label: "Organizadores", icon: ShieldCheck });
      items.push({ id: "checkin", label: "Portaria & Check-in", icon: ScanLine });
    }
    return items;
  }, [isStaffOrAdmin]);

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <button
        onClick={onBack}
        className="mb-4 inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground cursor-pointer"
      >
        <ArrowLeft className="h-4 w-4" /> Voltar ao Painel Geral
      </button>

      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="mb-1.5 flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-bold text-foreground">{event.name}</h1>
            {event.role && (
              <Badge tone={isAdmin ? "admin" : "staff"}>
                {isAdmin ? "Dono / Admin" : "Membro Staff"}
              </Badge>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5" /> {formatDateTime(event.date)}
            </span>
            <span className="flex items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5" /> {event.location}
            </span>
          </div>
        </div>

        {isAdmin && (
          <div className="flex flex-col items-end gap-1.5">
            {!confirmDelete ? (
              <Button variant="outline" size="sm" onClick={() => setConfirmDelete(true)}>
                <Trash2 className="h-4 w-4 text-destructive" /> Excluir Evento
              </Button>
            ) : (
              <div className="flex items-center gap-2 rounded-lg border border-destructive/20 bg-destructive/5 p-1.5">
                <span className="text-xs text-foreground font-medium pl-1">Excluir para sempre?</span>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleDeleteEvent}
                  disabled={deleteLoading}
                >
                  {deleteLoading ? <Spinner /> : "Sim"}
                </Button>
                <Button variant="ghost" size="sm" className="h-7 px-2" onClick={() => setConfirmDelete(false)}>
                  Não
                </Button>
              </div>
            )}
            {deleteError && <p className="text-xs text-destructive font-medium mt-1">{deleteError}</p>}
          </div>
        )}
      </div>

      {event.description && (
        <Card className="mb-6 p-4 bg-muted/30">
          <p className="text-sm text-foreground/90 whitespace-pre-wrap leading-relaxed">{event.description}</p>
        </Card>
      )}

      <div className="mb-6 flex gap-1 overflow-x-auto rounded-lg bg-muted p-1 border border-border/30">
        {tabList.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`inline-flex shrink-0 items-center gap-1.5 rounded-md px-3 py-2 text-xs font-semibold transition-all cursor-pointer ${
              tab === t.id
                ? "bg-background text-foreground shadow-xs"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <t.icon className="h-3.5 w-3.5" /> {t.label}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <Card className="p-5">
          <h3 className="mb-4 font-semibold text-sm uppercase tracking-wider text-muted-foreground">Métricas e Detalhes</h3>
          <dl className="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
            <div className="border-l-2 border-primary pl-3">
              <dt className="text-xs text-muted-foreground font-medium">Inscritos Totais</dt>
              <dd className="mt-0.5 text-xl font-bold text-foreground">{tickets.length}</dd>
            </div>
            <div className="border-l-2 border-emerald-500 pl-3">
              <dt className="text-xs text-muted-foreground font-medium">Presenças (Check-in)</dt>
              <dd className="mt-0.5 text-xl font-bold text-foreground">
                {tickets.filter((t) => t.checked_in).length}
              </dd>
            </div>
            <div className="col-span-2 border-l-2 border-neutral-300 dark:border-neutral-700 pl-3 sm:col-span-1">
              <dt className="text-xs text-muted-foreground font-medium">ID do Evento</dt>
              <dd className="mt-1 break-all font-mono text-[11px] text-foreground font-semibold bg-muted p-1 rounded">
                {event.id}
              </dd>
            </div>
          </dl>
          <div className="mt-6 border-t border-border/60 pt-4 text-xs text-muted-foreground flex items-start gap-2">
            <Info className="h-4 w-4 shrink-0 mt-0.5 text-primary" />
            <p>
              Divulgue o UUID estruturado acima. Qualquer usuário da plataforma pode utilizá-lo na área de buscas do painel para se inscrever ou cooperar.
            </p>
          </div>
        </Card>
      )}

      {tab === "ticket" && (
        <div className="space-y-4 max-w-md mx-auto">
          {isAdmin ? (
            <EmptyState
              icon={ShieldCheck}
              title="Você é o Organizador Principal"
              description="Como criador deste evento, você possui credenciais administrativas totais. Não é necessário emitir um ingresso de participação para você."
            />
          ) : myTicket ? (
            <TicketStub
              eventName={event.name}
              holderName={currentUser.name}
              code={myTicket.ticket_code}
              checkedIn={myTicket.checked_in}
            />
          ) : (
            <EmptyState
              icon={TicketIcon}
              title="Você não tem um bilhete de inscrição"
              description="Para participar da lista oficial de presença, emita seu convite individual."
              action={
                <Button size="sm" onClick={handleGetTicket} disabled={ticketActionLoading}>
                  {ticketActionLoading && <Spinner />}
                  Emitir Meu Ingresso Gratuitamente
                </Button>
              }
            />
          )}
          {ticketActionError && <Alert tone="error">{ticketActionError}</Alert>}
        </div>
      )}
      {tab === "participants" && isStaffOrAdmin && (
        <Card className="overflow-hidden">
          {ticketsLoading ? (
            <div className="flex justify-center py-14">
              <Spinner className="h-5 w-5 text-muted-foreground" />
            </div>
          ) : ticketsError ? (
            <div className="p-4">
              <Alert tone="error">{ticketsError}</Alert>
            </div>
          ) : tickets.length === 0 ? (
            <div className="p-4">
              <EmptyState icon={Users} title="A lista está vazia" description="Nenhum usuário emitiu ingressos para este evento até o momento." />
            </div>
          ) : (
            <ul className="divide-y divide-border">
              {tickets.map((t) => {
                const person = usersCache[t.attendee_id];
                return (
                  <li key={t.id} className="flex items-center justify-between gap-3 px-4 py-3 bg-card hover:bg-muted/10 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary text-xs font-semibold text-secondary-foreground border border-border">
                        {initials(person?.name || "?")}
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-foreground">
                          {person?.name || <span className="text-muted-foreground animate-pulse">Carregando dados...</span>}
                        </p>
                        {person?.email && <p className="text-[11px] text-muted-foreground">{person.email}</p>}
                      </div>
                    </div>
                    <div className="flex items-center">
                      {t.cancelled ? (
                        <Badge tone="danger">Cancelado</Badge>
                      ) : t.checked_in ? (
                        <Badge tone="success">Confirmado</Badge>
                      ) : (
                        <Badge tone="warn">Não Compareceu</Badge>
                      )}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </Card>
      )}

      {tab === "team" && isStaffOrAdmin && (
        <div className="space-y-6">
          {!myTicket ? (
            <EmptyState
              icon={ShieldCheck}
              title="Liberação Necessária"
              description="A verificação estruturada e inserção de novos membros da equipe requer a posse de um convite ativo atrelado à sua conta."
              action={
                <Button size="sm" onClick={handleGetTicket} disabled={ticketActionLoading}>
                  {ticketActionLoading && <Spinner />}
                  Vincular Meu Acesso Primeiro
                </Button>
              }
            />
          ) : (
            <>
              {isAdmin && (
                <Card className="p-5">
                  <h3 className="mb-1 flex items-center gap-2 text-sm font-semibold text-foreground">
                    <UserPlus className="h-4 w-4 text-primary" /> Recrutar Organizador
                  </h3>
                  <p className="mb-4 text-xs text-muted-foreground">
                    Digite o endereço eletrônico exato de um usuário cadastrado no sistema para delegar permissões Staff.
                  </p>
                  <div className="flex flex-col gap-2 sm:flex-row">
                    <Input
                      type="email"
                      placeholder="parceiro@email.com"
                      value={staffEmail}
                      onChange={(e) => setStaffEmail(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && staffEmail && handleAddStaff()}
                    />
                    <Button onClick={handleAddStaff} disabled={!staffEmail || staffLoading}>
                      {staffLoading ? <Spinner /> : <UserPlus className="h-4 w-4" />}
                      Promover
                    </Button>
                  </div>
                  {staffMsg && (
                    <div className="mt-3">
                      <Alert tone={staffMsg.tone}>{staffMsg.text}</Alert>
                    </div>
                  )}
                </Card>
              )}

              <Card className="overflow-hidden">
                <div className="border-b border-border bg-muted/40 px-5 py-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Corpo Organizacional</h3>
                </div>
                {organizersLoading ? (
                  <div className="flex justify-center py-14">
                    <Spinner className="h-5 w-5 text-muted-foreground" />
                  </div>
                ) : organizersError ? (
                  <div className="p-4">
                    <Alert tone="error">{organizersError}</Alert>
                  </div>
                ) : (
                  <ul className="divide-y divide-border">
                    {(organizers || []).map((org) => (
                      <li key={org.id} className="flex items-center justify-between px-5 py-3 text-xs bg-card">
                        <span className="font-mono text-foreground font-semibold">{org.email}</span>
                        <Badge tone={org.role === "admin" ? "admin" : "staff"}>
                          {org.role === "admin" ? "Dono" : "Staff Colaborador"}
                        </Badge>
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
            </>
          )}
        </div>
      )}
  {tab === "checkin" && isStaffOrAdmin && (
    <div className="grid gap-6 md:grid-cols-5 max-w-5xl mx-auto">
      {/* Formulário de Leitura / Entrada (Colunas: 2 de 5) */}
      <div className="md:col-span-2">
        <Card className="p-5">
          <h3 className="mb-1 flex items-center gap-2 text-sm font-semibold text-foreground">
            <ScanLine className="h-4 w-4 text-primary" /> Validar Entrada
          </h3>
          <p className="mb-4 text-xs text-muted-foreground">
            Insira o código alfanumérico do canhoto do ingresso apresentado pelo participante para registrar a presença imediata.
          </p>
          <div className="flex flex-col gap-2">
            <Input
              placeholder="Código do Ingresso (ex: TKT-123456)"
              value={checkinCode || ""}
              onChange={(e) => setCheckinCode(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && checkinCode && handleCheckIn()}
              className="font-mono uppercase placeholder:normal-case tracking-wider"
            />
            <Button className="w-full" onClick={handleCheckIn} disabled={!checkinCode || checkinLoading}>
              {checkinLoading ? <Spinner /> : <ScanLine className="h-4 w-4" />}
              Dar Check-in
            </Button>
          </div>
          {checkinResult && (
            <div className="mt-4 animate-in fade-in slide-in-from-top-2 duration-200">
              <Alert tone={checkinResult.tone}>{checkinResult.text}</Alert>
            </div>
          )}
        </Card>
      </div>

      {/* Histórico/Log de Check-ins (Colunas: 3 de 5) */}
      <div className="md:col-span-3">
        <Card className="overflow-hidden h-[400px] flex flex-col">
          <div className="border-b border-border bg-muted/40 px-5 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Fluxo de Entrada em Tempo Real
              </h3>
            </div>
            <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={loadCheckInLogs} disabled={logsLoading}>
              {logsLoading ? <Spinner /> : "Atualizar"}
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-border">
            {logsLoading && (!checkinLogs || checkinLogs.length === 0) ? (
              <div className="flex items-center justify-center h-full">
                <Spinner className="h-6 w-6 text-muted-foreground" />
              </div>
            ) : (!checkinLogs || checkinLogs.length === 0) ? (
              <div className="flex flex-col items-center justify-center h-full text-center p-6 text-muted-foreground">
                <Users className="h-8 w-8 mb-2 opacity-40" />
                <p className="text-sm font-medium">Nenhum check-in realizado ainda</p>
                <p className="text-xs max-w-[240px] mx-auto mt-1">
                  As entradas validadas aparecerão aqui listando quem liberou o acesso.
                </p>
              </div>
            ) : (
              checkinLogs.map((log) => {
                // Formatação segura da data caso formatDateTime não esteja escopado
                const dataFormatada = log?.checked_at 
                  ? new Date(log.checked_at).toLocaleString('pt-BR') 
                  : "Data pendente";

                return (
                  <div key={log?.id} className="p-4 hover:bg-muted/10 transition-colors flex items-center justify-between gap-4 animate-in fade-in duration-150">
                    <div className="space-y-1">
                      <p className="text-xs font-bold text-foreground font-mono uppercase tracking-wider">
                        {log?.ticket_code || "Ingresso n/a"}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Participante: <span className="font-semibold text-foreground">{log?.attendee_name || "Desconhecido"}</span>
                      </p>
                      <p className="text-[10px] text-muted-foreground/80 flex items-center gap-1">
                        Operador: <span className="font-mono bg-muted px-1.5 py-0.5 rounded text-[9px]">
                          {log?.checked_by_name || "Sistema"}
                        </span>
                      </p>
                    </div>
                    <div className="text-right">
                      <Badge tone="success" className="text-[10px] py-0.5 px-2">Liberado</Badge>
                      <p className="text-[10px] text-muted-foreground mt-1.5">
                        {dataFormatada}
                      </p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </Card>
      </div>
    </div>
  )}
</div>
  );
}


// ---------------------------------------------------------------------------
// Componente de Layout Superior: Header
// ---------------------------------------------------------------------------

function Header({ user, onLogout, onLogoClick }) {
  const { theme, setTheme } = useTheme();
  const isDark = theme === "dark" || (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4">
        <button onClick={onLogoClick} className="flex items-center gap-2 group text-left cursor-pointer">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-xs transition-transform group-hover:scale-105">
            <CalendarPlus className="h-4 w-4" />
          </div>
          <span className="font-bold text-foreground tracking-tight text-sm sm:text-base">EventosHub</span>
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setTheme(isDark ? "light" : "dark")}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-foreground cursor-pointer"
            aria-label="Trocar cor tema"
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>

          <div className="mx-1 hidden items-center gap-2 rounded-full border border-border py-1 pl-1 pr-3 sm:flex bg-muted/30">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
              {initials(user.name)}
            </div>
            <span className="text-xs font-medium text-foreground max-w-[120px] truncate">{user.name}</span>
          </div>

          <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-destructive h-9 w-9" onClick={onLogout} aria-label="Desconectar">
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}

// ---------------------------------------------------------------------------
// Ponto de Entrada Principal (Orquestrador Global)
// ---------------------------------------------------------------------------

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("ev_token"));
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem("ev_user");
    return saved ? JSON.parse(saved) : null;
  });

  const [view, setView] = useState("dashboard"); 
  const [selectedEvent, setSelectedEvent] = useState(null);

  const [events, setEvents] = useState([]);
  const [eventsLoading, setEventsLoading] = useState(false);
  const [eventsError, setEventsError] = useState("");

  // Handler que adiciona ou remove tokens e desloga em caso de erro 401
  const api = useCallback(
    (path, opts = {}) =>
      apiRequest(path, { ...opts, token: opts.token !== undefined ? opts.token : token }).catch(
        (e) => {
          if (e.status === 401) {
            localStorage.removeItem("ev_token");
            localStorage.removeItem("ev_user");
            setToken(null);
            setCurrentUser(null);
            setView("dashboard");
            setSelectedEvent(null);
          }
          throw e;
        }
      ),
    [token]
  );

  const loadEvents = useCallback(async () => {
    setEventsLoading(true);
    setEventsError("");
    try {
      const data = await api("/events/");
      setEvents(data.events);
    } catch (e) {
      setEventsError(e.message);
    } finally {
      setEventsLoading(false);
    }
  }, [api]);

  useEffect(() => {
    if (token) {
      loadEvents();
    }
  }, [token, loadEvents]);

  function handleAuthenticated(newToken, user) {
    localStorage.setItem("ev_token", newToken);
    localStorage.setItem("ev_user", JSON.stringify(user));
    setToken(newToken);
    setCurrentUser(user);
  }

  function handleLogout() {
    localStorage.removeItem("ev_token");
    localStorage.removeItem("ev_user");
    setToken(null);
    setCurrentUser(null);
    setView("dashboard");
    setSelectedEvent(null);
    setEvents([]);
  }

  function handleOpenEvent(event) {
    setSelectedEvent(event);
    setView("event");
  }

  function handleBackToDashboard() {
    setView("dashboard");
    setSelectedEvent(null);
    loadEvents();
  }

  return (
      <div className="min-h-screen bg-background font-sans text-foreground transition-colors duration-200">
        {!token || !currentUser ? (
          <AuthScreen api={api} onAuthenticated={handleAuthenticated} />
        ) : (
          <>
            <Header
              user={currentUser}
              onLogout={handleLogout}
              onLogoClick={handleBackToDashboard}
            />
            <main className="animate-in fade-in duration-300">
              {view === "dashboard" && (
                <Dashboard
                  api={api}
                  events={events}
                  eventsLoading={eventsLoading}
                  eventsError={eventsError}
                  onRefresh={loadEvents}
                  onOpenEvent={handleOpenEvent}
                />
              )}
              {view === "event" && selectedEvent && (
                <EventDetail
                  api={api}
                  event={selectedEvent}
                  currentUser={currentUser}
                  onBack={handleBackToDashboard}
                  onDeleted={handleBackToDashboard}
                />
              )}
            </main>
          </>
        )}
      </div>
  );
}
