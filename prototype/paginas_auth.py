# -*- coding: utf-8 -*-
"""Pantallas globales de acceso (compartidas por los tres roles)."""

from lib_css import CSS, LOGO_BLANCO, LOGO_COLOR, LOGO_COLOR_CSS
from lib_ui import ico

# En el panel de acceso hay espacio de sobra, asi que aqui si se muestra el
# lockup completo a tamano legible. El panel es navy, asi que va la variante
# monocroma. El artwork ya viene recortado a 2.0979:1 y sin fondo: por eso la
# caja no lleva fondo blanco ni borde, y la imagen usa height:auto.
LOGO_BIG = (
    '<span class="accede-logo">'
    '<img src="' + LOGO_BLANCO + '" width="600" height="286" decoding="async" '
    'alt="SGEMD, Emprendimiento Minuto de Dios"></span>'
)

_PUNTOS = [
    ("clipboard", "Diagnostico inicial y plan de trabajo por fases"),
    ("trend", "Seguimiento y tareas con evidencia adjunta"),
    ("chat", "Asesorias academicas y eventos de la institucion"),
]

_IZQ = """
<div class="auth-izq">
  <div>
    __LOGO__
  </div>
  <div>
    <h2 style="color:#ffffff;font-size:28px;line-height:1.2;max-width:420px">
      Gestion de clases de emprendimiento</h2>
    <p style="color:#ffffff;opacity:.78;font-size:14px;margin-top:14px;max-width:420px">
      Un solo lugar para diagnosticar, planificar, dar seguimiento y medir el avance
      de tu emprendimiento.</p>
    <div style="display:flex;flex-direction:column;gap:12px;margin-top:32px">__PUNTOS__</div>
  </div>
  <p style="color:#ffffff;opacity:.6;font-size:13px">Institucion Minuto de Dios &middot;
     Prototipo de interfaz</p>
</div>
"""

_PAG = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITULO__ — SGEMD</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>__CSS__
__LOGO_COLOR_CSS__
.auth{display:flex;min-height:100vh}
/* Panel navy. Esto vive en una clase y no en un style= en linea a proposito: un
   estilo inline gana a cualquier media query, asi que con el inline este panel
   no se ocultaba nunca en movil y empujaba el formulario fuera de pantalla. */
.auth-izq{flex:1;background:#051533;color:#ffffff;padding:56px 60px;
  display:flex;flex-direction:column;justify-content:space-between}
/* Lockup monocroma: el panel izquierdo es navy. Sin fondo ni borde porque el
   artwork ya viene recortado a 2.0979:1 y transparente. */
.accede-logo{display:block;width:260px}
.accede-logo img{width:100%;height:auto;display:block}
.auth-panel{flex:0 0 560px;background:#ffffff;padding:56px 60px;
  display:flex;align-items:center;justify-content:center}
.auth-panel>div{width:100%;max-width:__ANCHO__px}
/* A <=1023px el panel navy se oculta, asi que la marca pasa al panel blanco como
   barra compacta: sin esto el movil y la tablet entran sin logo. Se pinta con
   background y no con un segundo <img> para no duplicar el logo en el DOM.
   En panel blanco va la variante a color, no la monocroma. */
.auth-marca{display:none}
@media (max-width:1023px){
  .auth-izq{display:none}
  .auth-panel{flex:1 1 auto;padding:32px 20px;min-width:0}
  .auth-marca{display:block;width:170px;height:81px;margin:0 auto 22px;
    background-image:var(--logo-color-url);background-repeat:no-repeat;
    background-position:center;background-size:contain}
}
__ACCESO_CSS__
</style>
</head>
<body>
<div class="auth">__IZQ__<div class="auth-panel">
  <div><div class="auth-marca" role="img" aria-label="SGEMD, Emprendimiento Minuto de Dios"></div>__PASO__<h1>__TITULO__</h1>__CUERPO__</div>
</div></div>
<script>__JS__</script>
</body>
</html>
"""

# Estilos propios de las pantallas de acceso. Van aqui, y no en lib_css, porque
# solo las usan las cuatro pantallas de compartido/.
ACCESO_CSS = """
/* Avisos del formulario: uno por campo y uno general. El color no es el unico
   indicador, cada aviso lleva texto, y el general es un region role=alert. */
.acceso-error{margin:14px 0 0;padding:12px 14px;border-radius:8px;font-size:13px;
  font-weight:600;color:var(--tinta);background:var(--noche-04);
  border-left:4px solid var(--azul-real)}
.acceso-ok{margin:14px 0 0;padding:12px 14px;border-radius:8px;font-size:13px;
  font-weight:600;color:var(--tinta);background:var(--amarillo-14);
  border-left:4px solid var(--amarillo)}
.acceso-nota{margin-top:20px;font-size:13px;line-height:1.6;color:var(--tinta-2)}
.acceso-nota b{color:var(--tinta)}
.acceso-nota-centro{text-align:center}
.acceso-inicial{margin:8px 0 20px}
/* Nota de expiracion del codigo: comparte el tono de los avisos de sistema. */
.otp-nota{display:flex;align-items:center;gap:10px;margin-bottom:20px;padding:10px 14px;
  background:var(--noche-04);border:1px solid var(--gris);border-radius:8px;
  font-size:13px;line-height:1.5;color:var(--tinta-2)}
.otp-nota b{color:var(--tinta)}
.mt-24{margin-top:24px}
.fila-recordar{display:flex;align-items:center;justify-content:space-between;
  gap:12px;flex-wrap:wrap;margin:4px 0 22px}
.fila-recordar .chk{margin:0}
.fila-recordar a{font-size:13px;font-weight:600}
.ancho{width:100%}
/* Panel de credenciales de demostracion: es lo unico que hace que este
   prototipo se pueda recorrer sin backend, asi que se presenta como tal. */
.demo{margin-top:26px;border:1px solid var(--gris);border-radius:12px;
  background:var(--noche-02);padding:16px 18px}
.demo-t{font-size:13px;font-weight:700;color:var(--tinta);margin:0}
.demo-n{font-size:13px;color:var(--tinta-2);margin:4px 0 12px}
.demo-fila{display:flex;align-items:center;gap:12px;padding:10px 0;cursor:pointer;
  border-top:1px solid var(--noche-06)}
.demo-fila:first-of-type{border-top:0}
.demo-fila:hover{background:var(--azul-06)}
.demo-info{flex:1;min-width:0}
.demo-rol{font-size:14px;font-weight:600;color:var(--tinta)}
.demo-credencial{font-size:13px;color:var(--tinta-2);
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.demo-fila .btn{flex:0 0 auto}
@media (max-width:479px){
  .demo-fila{flex-wrap:wrap}
  .demo-fila .btn{width:100%}
}
"""

# Script de las cuatro pantallas de acceso. Es independiente de lib_js porque
# aqui no hay shell: no hay barra lateral, ni notificaciones, ni tabla. Lo que
# hace es validar, resolver el rol de las credenciales de demostracion y dejar
# la sesion en localStorage antes de redirigir.
AUTH_JS = r"""
(function () {
  "use strict";

  /* Las tres cuentas de demostracion acordadas. La contrasena coincide con el
     usuario; es un prototipo sin backend, no una politica de seguridad. */
  var CUENTAS = {
    estudiante: { rol: "Estudiante",    clave: "estudiante", destino: "../estudiante/dashboard.html" },
    profesor:   { rol: "Docente",       clave: "profesor",   destino: "../docente/dashboard.html" },
    admi:       { rol: "Administrador", clave: "admi",       destino: "../admin/dashboard.html" }
  };
  var CLAVE_SESION = "sgemd:sesion";
  var CLAVE_RECORDAR = "sgemd:recordar";

  function $(sel, raiz) { return (raiz || document).querySelector(sel); }
  function $$(sel, raiz) { return Array.prototype.slice.call((raiz || document).querySelectorAll(sel)); }

  function aviso(id, texto, clase) {
    var caja = document.getElementById(id);
    if (!caja) return;
    if (!texto) { caja.hidden = true; caja.textContent = ""; return; }
    caja.hidden = false;
    caja.className = clase;
    caja.textContent = texto;
  }
  function limpiar() {
    aviso("acceso-error", "");
    $$(".campo-error").forEach(function (x) { x.remove(); });
    $$("[aria-invalid]").forEach(function (c) { c.removeAttribute("aria-invalid"); });
  }
  function marcar(campo, texto) {
    limpiar();
    var caja = document.createElement("span");
    caja.className = "campo-error";
    caja.id = "err-" + campo.id;
    caja.textContent = texto;
    (campo.closest(".campo") || campo.parentNode).appendChild(caja);
    campo.setAttribute("aria-invalid", "true");
    campo.setAttribute("aria-describedby", caja.id);
    campo.focus();
  }

  /* --- panel de demostracion: un clic deja usuario y contrasena puestos --- */
  $$("[data-demo]").forEach(function (fila) {
    function usar() {
      var usuario = fila.dataset.demo;
      var dato = CUENTAS[usuario];
      if (!dato) return;
      var campoUsuario = document.getElementById("usuario");
      var campoClave = document.getElementById("clave");
      if (campoUsuario) campoUsuario.value = usuario;
      if (campoClave) campoClave.value = dato.clave;
      limpiar();
      $$("[data-demo]").forEach(function (o) { o.style.background = ""; });
      fila.style.background = "var(--amarillo-14)";
      if (campoClave) campoClave.focus();
    }
    fila.addEventListener("click", usar);
    fila.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); usar(); }
    });
  });

  /* --- recordar el ultimo usuario ---------------------------------------- */
  var recordar = document.getElementById("recordar");
  var campoUsuario = document.getElementById("usuario");
  try {
    var previo = localStorage.getItem(CLAVE_RECORDAR);
    if (previo && campoUsuario && !campoUsuario.value) {
      campoUsuario.value = previo;
      if (recordar) recordar.checked = true;
    }
  } catch (e) { /* localStorage bloqueado: el login sigue funcionando */ }

  /* --- formulario de acceso ---------------------------------------------- */
  var form = document.getElementById("acceso");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var clave = document.getElementById("clave");
      /* trim() y minusculas en el usuario: "  Estudiante " es el mismo usuario
         que "estudiante". La contrasena se respeta tal cual. */
      var usuario = (campoUsuario.value || "").trim().toLowerCase();
      var dato = CUENTAS[usuario];

      limpiar();
      if (!usuario) { marcar(campoUsuario, "Escribe tu usuario"); return; }
      if (!clave.value) { marcar(clave, "Escribe tu contrasena"); return; }
      if (!dato || clave.value !== dato.clave) {
        aviso("acceso-error",
          "Usuario o contrasena incorrectos. Usa una de las cuentas del panel de demostracion.",
          "acceso-error");
        /* El aviso es de formulario, no de un campo: se marca la contrasena como
           invalida y se la asocia al aviso, que es donde esta la explicacion. */
        clave.setAttribute("aria-invalid", "true");
        clave.setAttribute("aria-describedby", "acceso-error");
        campoUsuario.focus();
        return;
      }

      try {
        localStorage.setItem(CLAVE_SESION, JSON.stringify({
          rol: dato.rol, usuario: usuario, ingreso: new Date().toISOString()
        }));
        if (recordar && recordar.checked) localStorage.setItem(CLAVE_RECORDAR, usuario);
        else localStorage.removeItem(CLAVE_RECORDAR);
      } catch (x) { /* sin persistencia la redireccion sigue siendo valida */ }

      aviso("acceso-ok", "Sesion iniciada como " + dato.rol + ". Abriendo el panel...", "acceso-ok");
      window.setTimeout(function () { location.href = dato.destino; }, 600);
    });
  }

  /* --- registro, verificacion y recuperacion ------------------------------
     No tienen backend: validan lo obligatorio y confirman que el paso quedo
     simulado, sin Inventar un envio que no ocurre. */
  $$("form[data-form-simulado]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      limpiar();
      /* El codigo se valida como grupo: ocho campos de un digito. */
      var digitos = $$(".otp input", f);
      if (digitos.length) {
        for (var k = 0; k < digitos.length; k++) {
          if (!digitos[k].value.trim()) { marcar(digitos[k], "Faltan digitos del codigo"); return; }
        }
      }
      for (var i = 0; i < f.elements.length; i++) {
        var c = f.elements[i];
        /* Solo los marcados como obligatorios se validan: botones y campos
           opcionales se dejan pasar. Las casillas se miran por su estado, no
           por su valor: "on" sigue siendo cierto aunque este sin marcar. */
        if (!c.required) continue;
        var vacio = c.type === "checkbox" ? !c.checked : !c.value.trim();
        if (vacio) { marcar(c, "Este campo es obligatorio"); return; }
      }
      aviso("acceso-ok", f.dataset.mensaje || "Listo. En el prototipo este paso se simula aqui.", "acceso-ok");
      var destino = f.dataset.destino;
      if (destino) window.setTimeout(function () { location.href = destino; }, 700);
    });
  });

  /* --- codigo de 8 digitos: el foco avanza y atrasa solo ------------------ */
  var digitos = $$(".otp input");
  if (digitos.length) {
    digitos.forEach(function (d, i) {
      d.addEventListener("input", function () {
        d.value = d.value.replace(/\D/g, "").slice(-1);
        if (d.value && digitos[i + 1]) digitos[i + 1].focus();
      });
      d.addEventListener("keydown", function (e) {
        if (e.key === "Backspace" && !d.value && digitos[i - 1]) digitos[i - 1].focus();
      });
      d.addEventListener("paste", function (e) {
        var texto = (e.clipboardData || window.clipboardData).getData("text").replace(/\D/g, "");
        if (!texto) return;
        e.preventDefault();
        digitos.forEach(function (otro, k) { otro.value = texto[k] || ""; });
        (digitos[texto.length] || digitos[digitos.length - 1]).focus();
      });
    });
    digitos[0].focus();
  }

  /* --- botones sueltos con data-accion (reenviar codigo) ------------------ */
  document.addEventListener("click", function (e) {
    var b = e.target.closest("button[data-accion]");
    if (!b) return;
    if (b.dataset.accion === "reenviar") {
      aviso("acceso-ok", "Codigo reenviado a tu correo institucional.", "acceso-ok");
    }
  });
})();
"""


def auth_shell(titulo, cuerpo, paso=None, paso_txt=None, ancho=460):
    puntos = "".join(
        '<div style="display:flex;align-items:flex-start;gap:10px;font-size:13px;'
        'color:#ffffff;opacity:.85"><span style="color:#ffd300;flex:0 0 18px">'
        + ico(n, 16) + "</span><span>" + t + "</span></div>"
        for n, t in _PUNTOS
    )
    izq = _IZQ.replace("__LOGO__", LOGO_BIG).replace("__PUNTOS__", puntos)

    cab = ""
    if paso is not None:
        barras = "".join(
            '<div style="flex:1;height:4px;border-radius:999px;background:'
            + ("#ffd300" if i == paso else "#bbbbbb") + '"></div>'
            for i in range(paso + 1)
        )
        cab = '<div style="display:flex;align-items:center;gap:8px;margin-bottom:28px">' + barras + "</div>"
        if paso_txt:
            cab += '<p style="font-size:13px;color:#162644;margin-bottom:20px">' + paso_txt + "</p>"

    html = (
        _PAG.replace("__TITULO__", titulo)
        .replace("__CSS__", CSS)
        .replace("__LOGO_COLOR_CSS__", LOGO_COLOR_CSS)
        .replace("__ACCESO_CSS__", ACCESO_CSS)
        .replace("__JS__", AUTH_JS)
        .replace("__IZQ__", izq)
        .replace("__ANCHO__", str(ancho))
        .replace("__PASO__", cab)
        .replace("__CUERPO__", cuerpo)
    )
    return html


_CUENTAS_DEMO = [
    ("estudiante", "Estudiante"),
    ("profesor", "Docente"),
    ("admi", "Administrador"),
]


def _filas_demo():
    """Filas del panel de demostracion. El texto de la credencial va en el DOM
    a proposito: es un prototipo que se recorre sin backend y quien lo lea
    necesita ver como entrar."""
    filas = []
    for usuario, rol in _CUENTAS_DEMO:
        filas.append(
            '<div class="demo-fila" data-demo="%s" role="button" tabindex="0" '
            'aria-label="Usar la cuenta de demostracion %s">'
            '<div class="demo-info"><div class="demo-rol">%s</div>'
            '<div class="demo-credencial">%s / %s</div></div>'
            '<button type="button" class="btn btn-secundario btn-sm">Usar</button>'
            "</div>" % (usuario, rol, rol, usuario, usuario)
        )
    return "".join(filas)


def login():
    cuerpo = """
<p class="acceso-nota">Ingresa con tu usuario y contrasena. Tu rol se determina
  automaticamente y abre el panel que le corresponde.</p>
<form id="acceso" novalidate>
  <div class="campo"><label for="usuario">Usuario<span class="req">*</span></label>
    <input id="usuario" name="usuario" type="text" autocomplete="username"
      autocapitalize="none" spellcheck="false" placeholder="Ej. estudiante" required></div>
  <div class="campo"><label for="clave">Contrasena<span class="req">*</span></label>
    <input id="clave" name="clave" type="password" autocomplete="current-password"
      placeholder="Tu contrasena" required></div>
  <div class="fila-recordar">
    <label class="chk"><input id="recordar" type="checkbox" checked> Recordarme</label>
    <a href="recuperar-contrasena.html">Olvide mi contrasena</a>
  </div>
  <button class="btn btn-primario ancho" type="submit">Ingresar al sistema</button>
</form>
<div id="acceso-error" class="acceso-error" role="alert" hidden></div>
<div id="acceso-ok" class="acceso-ok" role="status" hidden></div>
<section class="demo" aria-labelledby="demo-t">
  <p class="demo-t" id="demo-t">Cuentas de demostracion</p>
  <p class="demo-n">Pulsa una fila para completar el formulario. El prototipo valida
    en el navegador, sin servidor.</p>
  __FILAS__
</section>
<p class="acceso-nota">No tienes cuenta? <a href="registro.html"><b>Registrate aqui</b></a></p>
"""
    return auth_shell(
        "Iniciar sesion",
        cuerpo.replace("__FILAS__", _filas_demo()),
    )


def registro():
    cuerpo = """
<p class="acceso-nota acceso-inicial">Completa tus datos. Recibiras un codigo de verificacion de 8 digitos en tu correo institucional.</p>
<form data-form-simulado novalidate data-mensaje="Cuenta creada. Revisa tu correo institucional para el codigo de verificacion." data-destino="verificar-otp.html">
<div class="grid g-2" style="gap:0 16px">
  <div class="campo"><label for="n1">Nombres<span class="req">*</span></label>
    <input id="n1" type="text" placeholder="Ej. Mariana" required></div>
  <div class="campo"><label for="n2">Apellidos<span class="req">*</span></label>
    <input id="n2" type="text" placeholder="Ej. Lopez Herrera" required></div>
</div>
<div class="campo"><label for="ti">Tipo y numero de documento<span class="req">*</span></label>
  <div style="display:flex;gap:10px">
    <select id="ti" style="flex:0 0 150px"><option>CC</option><option>CE</option><option>TI</option></select>
    <input type="text" placeholder="1020304050" style="flex:1" required></div></div>
<div class="campo"><label for="ce">Correo personal<span class="req">*</span></label>
  <input id="ce" type="email" placeholder="mariana@correo.com" required></div>
<div class="campo"><label for="ci">Correo institucional<span class="req">*</span></label>
  <input id="ci" type="email" placeholder="mariana@minutodedios.edu.co" required>
  <div class="ayuda">__ICO_MAIL__ Aqui recibiras las notificaciones del sistema.</div></div>
<div class="grid g-2" style="gap:0 16px">
  <div class="campo"><label for="tf">Telefono fijo</label>
    <input id="tf" type="tel" placeholder="604 123 4567"></div>
  <div class="campo"><label for="tc">Celular<span class="req">*</span></label>
    <input id="tc" type="tel" placeholder="300 123 4567" required></div>
</div>
<div class="campo"><label for="pa">Contrasena<span class="req">*</span></label>
  <input id="pa" type="password" placeholder="Minimo 8 caracteres" required>
  <div class="ayuda">__ICO_ESCUDO__ Debe incluir mayuscula, minuscula, numero y simbolo.</div></div>
<label class="chk"><input type="checkbox" required> Acepto el tratamiento de mis datos personales y la
  politica de privacidad de la institucion</label>
<label class="chk"><input type="checkbox"> Confirmo que los datos registrados son veraces</label>
<button class="btn btn-acento ancho" type="submit">Crear cuenta y verificarme</button>
</form>
<div id="acceso-ok" class="acceso-ok" role="status" hidden></div>
<p class="acceso-nota acceso-nota-centro">Ya tienes cuenta?
  <a href="login.html"><b>Inicia sesion</b></a></p>
"""
    return auth_shell(
        "Crear mi cuenta",
        cuerpo.replace("__ICO_MAIL__", ico("mail", 13)).replace("__ICO_ESCUDO__", ico("escudo", 13)),
    )


def verificar_otp():
    cuerpo = """
<p class="acceso-nota acceso-inicial">Ingresa el codigo de 8 digitos que enviamos a
  <b>mariana.lopez@minutodedios.edu.co</b></p>
<form data-form-simulado novalidate data-mensaje="Codigo verificado. Tu perfil queda en estado Limitado hasta que un administrador active la cuenta.">
<div class="otp" role="group" aria-labelledby="otp-titulo" style="margin-bottom:18px">
  <input class="otp-d" type="text" inputmode="numeric" maxlength="1" aria-label="Digito 1">
  <input class="otp-d" type="text" inputmode="numeric" maxlength="1" aria-label="Digito 2">
  <input class="otp-d" type="text" inputmode="numeric" maxlength="1" aria-label="Digito 3">
  <input class="otp-d" type="text" inputmode="numeric" maxlength="1" aria-label="Digito 4">
  <input class="otp-d" type="text" inputmode="numeric" maxlength="1" aria-label="Digito 5">
  <input class="otp-d" type="text" inputmode="numeric" maxlength="1" aria-label="Digito 6">
  <input class="otp-d" type="text" inputmode="numeric" maxlength="1" aria-label="Digito 7">
  <input class="otp-d" type="text" inputmode="numeric" maxlength="1" aria-label="Digito 8">
</div>
<button class="btn btn-primario ancho" type="submit">Verificar mi cuenta</button>
</form>
<div class="otp-nota">__ICO_RELOJ__
  <span>El codigo expira en <b>04:32</b> minutos.</span></div>
<div class="fila-recordar">
  <a href="registro.html">Volver al registro</a>
  <span>No recibiste el codigo?</span>
  <button class="btn btn-secundario btn-sm" type="button" data-accion="reenviar">Reenviar codigo</button>
</div>
<div id="acceso-ok" class="acceso-ok" role="status" hidden></div>
<div class="callout mt-24">__ICO_ALERTA__
  <div>Al verificar tu correo, tu perfil queda en estado <b>Limitado</b>: podras entrar al
  sistema, pero los modulos de Diagnostico, Tareas y Asesorias permaneceran bloqueados
  hasta que un administrador active tu cuenta.</div></div>
"""
    return auth_shell(
        "Verifica tu correo",
        cuerpo.replace("__ICO_RELOJ__", ico("reloj", 16)).replace("__ICO_ALERTA__", ico("alerta", 18)),
        paso=1,
        paso_txt="Paso 2 de 2 &middot; Codigo de verificacion",
    )


def recuperar_contrasena():
    cuerpo = """
<p class="acceso-nota acceso-inicial">Indica el correo con el que te registraste y te enviaremos un enlace para restablecer
  tu contrasena.</p>
<form data-form-simulado novalidate data-mensaje="Si el correo y el documento coinciden, en unos minutos llega el enlace de restablecimiento.">
<div class="campo"><label for="co">Correo registrado<span class="req">*</span></label>
  <input id="co" type="email" placeholder="nombre@minutodedios.edu.co" required>
  <div class="ayuda">__ICO_MAIL__ Puedes usar tu correo institucional o tu correo personal.</div></div>
<div class="campo"><label for="do">Numero de documento<span class="req">*</span></label>
  <input id="do" type="text" placeholder="1020304050" required></div>
<button class="btn btn-primario ancho" type="submit">Enviar enlace de recuperacion</button>
</form>
<div id="acceso-ok" class="acceso-ok" role="status" hidden></div>
<div class="callout mt-24">__ICO_ESCUDO__
  <div>Por seguridad el enlace caduca en 30 minutos. Si no lo recibes, comunicate con la
  coordinacion academica de tu programa.</div></div>
<p class="acceso-nota acceso-nota-centro">Recordaste la contrasena?
  <a href="login.html"><b>Inicia sesion</b></a></p>
"""
    return auth_shell(
        "Recuperar contrasena",
        cuerpo.replace("__ICO_MAIL__", ico("mail", 13)).replace("__ICO_ESCUDO__", ico("escudo", 18)),
    )