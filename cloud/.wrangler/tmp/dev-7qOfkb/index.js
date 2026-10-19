var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// src/store.js
function createStore(env) {
  return env.DB_API_URL ? createHttpStore(env) : createKvStore(env);
}
__name(createStore, "createStore");
function createHttpStore(env) {
  async function call(action, payload = {}) {
    const resp = await fetch(env.DB_API_URL.trim(), {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Api-Secret": (env.DB_API_SECRET || "").trim() },
      body: JSON.stringify({ action, ...payload }),
      signal: AbortSignal.timeout(8e3)
    });
    if (resp.status === 409) throw new Error("duplicate");
    if (!resp.ok) throw new Error(`DB API ${action}: ${resp.status}`);
    return (await resp.json()).result;
  }
  __name(call, "call");
  return {
    getUserByEmail: /* @__PURE__ */ __name((email) => call("user_get", { email }), "getUserByEmail"),
    createUser: /* @__PURE__ */ __name((user) => call("user_create", { user }), "createUser"),
    createSession: /* @__PURE__ */ __name((tokenHash, data, ttl) => call("session_create", { tokenHash, data, ttl }), "createSession"),
    getSession: /* @__PURE__ */ __name((tokenHash) => call("session_get", { tokenHash }), "getSession"),
    deleteSession: /* @__PURE__ */ __name((tokenHash) => call("session_delete", { tokenHash }), "deleteSession"),
    addHistory: /* @__PURE__ */ __name((uid, entry) => call("history_add", { uid, entry }), "addHistory"),
    listHistory: /* @__PURE__ */ __name((uid, limit = 100) => call("history_list", { uid, limit }), "listHistory"),
    deleteHistory: /* @__PURE__ */ __name((uid, id) => call("history_delete", { uid, id }), "deleteHistory"),
    clearHistory: /* @__PURE__ */ __name((uid) => call("history_clear", { uid }), "clearHistory"),
    getFailures: /* @__PURE__ */ __name((email) => call("fail_get", { email }), "getFailures"),
    setFailures: /* @__PURE__ */ __name((email, count, ttl) => call("fail_set", { email, count, ttl }), "setFailures"),
    clearFailures: /* @__PURE__ */ __name((email) => call("fail_clear", { email }), "clearFailures")
  };
}
__name(createHttpStore, "createHttpStore");
function createKvStore(env) {
  const kv = env.PHOTOS;
  const REVERSE_MAX = 9999999999999;
  return {
    async getUserByEmail(email) {
      return kv.get(`user:${email}`, "json");
    },
    async createUser(user) {
      await kv.put(`user:${user.email}`, JSON.stringify(user));
    },
    async createSession(tokenHash, data, ttlSeconds) {
      await kv.put(`sess:${tokenHash}`, JSON.stringify(data), { expirationTtl: ttlSeconds });
    },
    async getSession(tokenHash) {
      return kv.get(`sess:${tokenHash}`, "json");
    },
    async deleteSession(tokenHash) {
      await kv.delete(`sess:${tokenHash}`);
    },
    // A chave usa o tempo invertido: o KV lista em ordem crescente, então o mais novo vem primeiro
    async addHistory(uid, entry) {
      const ts = Date.now();
      const id = `${String(REVERSE_MAX - ts).padStart(13, "0")}${crypto.randomUUID().slice(0, 6)}`;
      const saved = { ...entry, id, ts };
      await kv.put(`hist:${uid}:${id}`, JSON.stringify(saved));
      return saved;
    },
    async listHistory(uid, limit = 100) {
      const listed = await kv.list({ prefix: `hist:${uid}:`, limit });
      const items = await Promise.all(listed.keys.map((k) => kv.get(k.name, "json")));
      return items.filter(Boolean);
    },
    async deleteHistory(uid, id) {
      await kv.delete(`hist:${uid}:${id}`);
    },
    async clearHistory(uid) {
      const listed = await kv.list({ prefix: `hist:${uid}:`, limit: 1e3 });
      await Promise.all(listed.keys.map((k) => kv.delete(k.name)));
    },
    async getFailures(email) {
      return await kv.get(`fail:${email}`, "json") || 0;
    },
    async setFailures(email, count, ttlSeconds) {
      await kv.put(`fail:${email}`, JSON.stringify(count), { expirationTtl: ttlSeconds });
    },
    async clearFailures(email) {
      await kv.delete(`fail:${email}`);
    }
  };
}
__name(createKvStore, "createKvStore");

// src/auth.js
var COOKIE = "sv_session";
var SESSION_TTL = 7 * 24 * 3600;
var PBKDF2_ITERS = 1e5;
var MAX_FAILS = 8;
var FAIL_WINDOW = 15 * 60;
var MAX_HISTORY_TEXT = 200;
var json = /* @__PURE__ */ __name((data, status = 200, headers = {}) => new Response(JSON.stringify(data), {
  status,
  headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...headers }
}), "json");
var b64 = /* @__PURE__ */ __name((bytes) => btoa(String.fromCharCode(...bytes)), "b64");
var unb64 = /* @__PURE__ */ __name((str) => Uint8Array.from(atob(str), (c) => c.charCodeAt(0)), "unb64");
var b64url = /* @__PURE__ */ __name((bytes) => b64(bytes).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""), "b64url");
async function pbkdf2(password, salt, iters) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt, iterations: iters }, key, 256);
  return new Uint8Array(bits);
}
__name(pbkdf2, "pbkdf2");
function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a[i] ^ b[i];
  return diff === 0;
}
__name(safeEqual, "safeEqual");
async function sha256Hex(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
__name(sha256Hex, "sha256Hex");
function getCookie(req, name) {
  const header = req.headers.get("Cookie") || "";
  for (const part of header.split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return null;
}
__name(getCookie, "getCookie");
var sessionCookie = /* @__PURE__ */ __name((token, maxAge) => `${COOKIE}=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=${maxAge}`, "sessionCookie");
async function readBody(req) {
  const text = await req.text();
  if (text.length > 4096) throw new Error("Corpo grande demais");
  try {
    return JSON.parse(text || "{}");
  } catch {
    throw new Error("JSON inv\xE1lido");
  }
}
__name(readBody, "readBody");
function sameOrigin(req, url) {
  const origin = req.headers.get("Origin");
  return !origin || origin === url.origin;
}
__name(sameOrigin, "sameOrigin");
var validEmail = /* @__PURE__ */ __name((e) => /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,}$/.test(e), "validEmail");
async function currentUser(req, store) {
  const token = getCookie(req, COOKIE);
  if (!token) return null;
  const session = await store.getSession(await sha256Hex(token));
  return session ? { id: session.uid, email: session.email, name: session.name } : null;
}
__name(currentUser, "currentUser");
async function startSession(store, user) {
  const token = b64url(crypto.getRandomValues(new Uint8Array(32)));
  await store.createSession(await sha256Hex(token), { uid: user.id, email: user.email, name: user.name }, SESSION_TTL);
  return sessionCookie(token, SESSION_TTL);
}
__name(startSession, "startSession");
async function register(req, store) {
  const body = await readBody(req);
  const name = String(body.name || "").trim().slice(0, 60);
  const email = String(body.email || "").trim().toLowerCase();
  const password = String(body.password || "");
  if (!name) return json({ error: "Informe seu nome." }, 400);
  if (!validEmail(email)) return json({ error: "E-mail inv\xE1lido." }, 400);
  if (password.length < 8 || password.length > 128) return json({ error: "A senha precisa ter de 8 a 128 caracteres." }, 400);
  if (await store.getUserByEmail(email)) return json({ error: "Este e-mail j\xE1 tem cadastro. Entre na sua conta." }, 409);
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const hash = await pbkdf2(password, salt, PBKDF2_ITERS);
  const user = { id: crypto.randomUUID(), email, name, salt: b64(salt), hash: b64(hash), iters: PBKDF2_ITERS, createdAt: Date.now() };
  try {
    await store.createUser(user);
  } catch (e) {
    if (String(e.message).includes("duplicate")) return json({ error: "Este e-mail j\xE1 tem cadastro. Entre na sua conta." }, 409);
    throw e;
  }
  return json({ ok: true });
}
__name(register, "register");
async function login(req, store) {
  const body = await readBody(req);
  const email = String(body.email || "").trim().toLowerCase();
  const password = String(body.password || "");
  const generic = { error: "E-mail ou senha incorretos." };
  if (!validEmail(email) || !password) return json(generic, 401);
  if (await store.getFailures(email) >= MAX_FAILS) {
    return json({ error: "Muitas tentativas. Tente de novo em 15 minutos." }, 429);
  }
  const user = await store.getUserByEmail(email);
  const salt = user ? unb64(user.salt) : new Uint8Array(16);
  const hash = await pbkdf2(password, salt, user ? user.iters : PBKDF2_ITERS);
  if (!user || !safeEqual(hash, unb64(user.hash))) {
    await store.setFailures(email, await store.getFailures(email) + 1, FAIL_WINDOW);
    return json(generic, 401);
  }
  await store.clearFailures(email);
  const cookie = await startSession(store, user);
  return json({ user: { name: user.name, email: user.email } }, 200, { "Set-Cookie": cookie });
}
__name(login, "login");
async function logout(req, store) {
  const token = getCookie(req, COOKIE);
  if (token) await store.deleteSession(await sha256Hex(token));
  return json({ ok: true }, 200, { "Set-Cookie": sessionCookie("", 0) });
}
__name(logout, "logout");
async function addHistory(req, store, user) {
  const body = await readBody(req);
  const entry = {
    display: String(body.display || "").slice(0, MAX_HISTORY_TEXT),
    // ex.: "√9 + 2^3 = 11"
    expr: String(body.expr || "").slice(0, MAX_HISTORY_TEXT),
    // o que foi digitado/lido
    source: body.source === "foto" ? "foto" : "teclado"
  };
  if (!entry.display || !entry.expr) return json({ error: "Conta vazia." }, 400);
  return json({ entry: await store.addHistory(user.id, entry) });
}
__name(addHistory, "addHistory");
async function handleAuthRoutes(req, env, url) {
  const p = url.pathname;
  if (!p.startsWith("/api/auth/") && !p.startsWith("/api/history")) return null;
  const store = createStore(env);
  const isWrite = req.method !== "GET";
  if (isWrite && !sameOrigin(req, url)) return json({ error: "Origem n\xE3o permitida." }, 403);
  try {
    if (req.method === "POST" && p === "/api/auth/register") return await register(req, store);
    if (req.method === "POST" && p === "/api/auth/login") return await login(req, store);
    if (req.method === "POST" && p === "/api/auth/logout") return await logout(req, store);
    const user = await currentUser(req, store);
    if (req.method === "GET" && p === "/api/auth/me") {
      return user ? json({ user: { name: user.name, email: user.email } }) : json({ user: null }, 401);
    }
    if (p.startsWith("/api/history")) {
      if (!user) return json({ error: "Entre na sua conta." }, 401);
      if (req.method === "GET" && p === "/api/history") return json({ items: await store.listHistory(user.id, 100) });
      if (req.method === "POST" && p === "/api/history") return await addHistory(req, store, user);
      if (req.method === "DELETE" && p === "/api/history") {
        await store.clearHistory(user.id);
        return json({ ok: true });
      }
      if (req.method === "DELETE" && p.startsWith("/api/history/")) {
        await store.deleteHistory(user.id, decodeURIComponent(p.slice("/api/history/".length)));
        return json({ ok: true });
      }
    }
    return json({ error: "Rota n\xE3o encontrada." }, 404);
  } catch (e) {
    console.error(e);
    return json({ error: "N\xE3o foi poss\xEDvel concluir. Tente de novo." }, 400);
  }
}
__name(handleAuthRoutes, "handleAuthRoutes");

// src/index.js
var MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"];
var MAX_BYTES = 5 * 1024 * 1024;
var PROMPT = `Voc\xEA \xE9 um OCR especializado em exerc\xEDcios matem\xE1ticos escolares.
Analise a imagem e leia a express\xE3o matem\xE1tica principal (manuscrita ou impressa).
Responda APENAS com a express\xE3o em TEXTO SIMPLES, sem LaTeX, sem "$", sem "=" e sem o resultado.
Use somente: n\xFAmeros, + - * / , ^ para pot\xEAncia, sqrt(x) para raiz quadrada e par\xEAnteses ( ).
Exemplos de resposta: 3 + 2 | (4 + 2) * 3 | sqrt(9) + 2^3 | ((1 - 1) + 2) / 2
Se houver v\xE1rias contas, responda s\xF3 a mais destacada ou a primeira.
Se n\xE3o houver nenhuma express\xE3o matem\xE1tica clara, responda apenas: NENHUMA`;
var json2 = /* @__PURE__ */ __name((data, status = 200) => new Response(JSON.stringify(data), {
  status,
  headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" }
}), "json");
function toBase64(buf) {
  const bytes = new Uint8Array(buf);
  let s = "";
  for (let i = 0; i < bytes.length; i += 32768) {
    s += String.fromCharCode.apply(null, bytes.subarray(i, i + 32768));
  }
  return btoa(s);
}
__name(toBase64, "toBase64");
async function handleUpload(req, env) {
  if (!env.UPLOAD_TOKEN || req.headers.get("X-Token") !== env.UPLOAD_TOKEN) {
    return json2({ status: "error", message: "Token inv\xE1lido" }, 401);
  }
  const body = await req.arrayBuffer();
  if (body.byteLength < 1e3) return json2({ status: "error", message: "Corpo vazio ou pequeno demais" }, 400);
  if (body.byteLength > MAX_BYTES) return json2({ status: "error", message: "Foto grande demais (m\xE1x 5 MB)" }, 413);
  const filename = (req.headers.get("X-Filename") || `captura_${Date.now()}.jpg`).replace(/[^\w.\-]/g, "_").slice(0, 80);
  const meta = { filename, timestamp: Date.now() / 1e3, size: body.byteLength };
  await env.PHOTOS.put("latest", body);
  await env.PHOTOS.put("meta", JSON.stringify(meta));
  return json2({ status: "ok", filename });
}
__name(handleUpload, "handleUpload");
async function handleStatus(env) {
  const meta = await env.PHOTOS.get("meta", "json");
  return json2({
    status: "ok",
    has_photo: !!meta,
    timestamp: meta?.timestamp ?? 0,
    filename: meta?.filename ?? null
  });
}
__name(handleStatus, "handleStatus");
async function handleOcr(env) {
  const photo = await env.PHOTOS.get("latest", "arrayBuffer");
  if (!photo) return json2({ status: "empty", message: "Nenhuma foto dispon\xEDvel." }, 404);
  const apiKey = (env.GEMINI_API_KEY || "").trim();
  if (!apiKey) return json2({ status: "error", message: "GEMINI_API_KEY n\xE3o configurada" }, 500);
  const body = JSON.stringify({
    contents: [{
      parts: [
        { inline_data: { mime_type: "image/jpeg", data: toBase64(photo) } },
        { text: PROMPT }
      ]
    }],
    // Resposta curta: a tarefa é só ler "3 + 2" (folga de tokens p/ modelos que "pensam")
    generationConfig: { temperature: 0, maxOutputTokens: 256 }
  });
  const t0 = Date.now();
  let resp;
  let used = "";
  for (let tentativa = 1; tentativa <= MODELS.length; tentativa++) {
    const MODEL = MODELS[tentativa - 1];
    try {
      resp = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${encodeURIComponent(apiKey)}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body,
          signal: AbortSignal.timeout(15e3)
        }
      );
    } catch (e) {
      console.error("Gemini timeout/erro de rede", tentativa, String(e));
      resp = null;
      continue;
    }
    used = MODEL;
    if (![503, 429, 404].includes(resp.status)) break;
  }
  if (!resp) {
    return json2({ status: "error", message: "Gemini n\xE3o respondeu a tempo", ms: Date.now() - t0 }, 504);
  }
  if (!resp.ok) {
    const detail = await resp.text();
    console.error("Gemini erro", resp.status, detail);
    return json2({ status: "error", message: `Gemini respondeu ${resp.status}`, ms: Date.now() - t0, detail: detail.slice(0, 400) }, 502);
  }
  const data = await resp.json();
  const text = data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || "";
  return json2({ status: "ok", text, model: used });
}
__name(handleOcr, "handleOcr");
var src_default = {
  async fetch(req, env) {
    const url = new URL(req.url);
    const { pathname } = url;
    try {
      const authResponse = await handleAuthRoutes(req, env, url);
      if (authResponse) return authResponse;
      if (req.method === "POST" && pathname === "/api/upload") return await handleUpload(req, env);
      if (req.method === "GET" && pathname === "/api/status") return await handleStatus(env);
      if (req.method === "POST" && pathname === "/api/ocr") return await handleOcr(env);
      return json2({ status: "error", message: "Rota n\xE3o encontrada" }, 404);
    } catch (e) {
      console.error(e);
      return json2({ status: "error", message: String(e) }, 500);
    }
  }
};

// ../../../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// ../../../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    const body = JSON.stringify(error);
    const headers = {
      "Content-Type": "application/json",
      "MF-Experimental-Error-Stack": "true"
    };
    const encoded = encodeURIComponent(body);
    if (encoded.length <= 8192) {
      headers["MF-Experimental-Error-Stack-Payload"] = encoded;
    }
    return new Response(body, { status: 500, headers });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-7u5Ft7/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = src_default;

// ../../../../AppData/Local/npm-cache/_npx/32026684e21afda6/node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-7u5Ft7/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class ___Facade_ScheduledController__ {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  scheduledTime;
  cron;
  static {
    __name(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=index.js.map
