# -*- coding: utf-8 -*-
"""Tokens y estilos base del prototipo SGEMD.

Paleta ABSOLUTA: solo 6 hex. Cualquier otro color esta prohibido.
Las unicas excepciones son variantes rgba() derivadas de esos mismos tokens.
"""

# El logo va incrustado como data URI y no como archivo suelto: Stitch sirve cada
# pantalla como un documento aislado, asi que una ruta relativa a _marca/ daria 404
# dentro del proyecto. Se generan con _marca/preparar_logo.py.
from logo_datos import LOGO_BLANCO_URI, LOGO_COLOR_URI  # noqa: E402

# Variante monocroma, para fondos navy.
LOGO_BLANCO = LOGO_BLANCO_URI
# Variante a color con el blanco del logotipo passage a #051533, para fondos claros.
LOGO_COLOR = LOGO_COLOR_URI

# --- Tokens -----------------------------------------------------------------
T = {
    "amarillo": "#ffd300",
    "blanco": "#ffffff",
    "azul_profundo": "#162644",
    "azul_noche": "#051533",
    "azul_real": "#004a93",
    "gris": "#bbbbbb",
}

TOKENS_CSS = """
:root{
  --amarillo:#ffd300; --blanco:#ffffff; --azul-profundo:#162644;
  --azul-noche:#051533; --azul-real:#004a93; --gris:#bbbbbb;
  --tinta:#051533; --tinta-2:#162644;
  --linea:#bbbbbb;
  --azul-06:rgba(0,74,147,.06); --azul-12:rgba(0,74,147,.12);
  --azul-28:rgba(0,74,147,.28); --azul-15:rgba(0,74,147,.15);
  --azul-08:rgba(0,74,147,.08);
  --noche-02:rgba(5,21,51,.02); --noche-03:rgba(5,21,51,.03);
  --noche-04:rgba(5,21,51,.04); --noche-06:rgba(5,21,51,.06);
  --noche-55:rgba(5,21,51,.55); --noche-28:rgba(5,21,51,.28);
  --amarillo-14:rgba(255,211,0,.14); --blanco-08:rgba(255,255,255,.08);
  --r-sm:8px; --r-md:12px; --r-full:999px;
  --s-1:8px; --s-2:16px; --s-3:24px; --s-4:32px; --s-5:40px; --s-6:48px;
  --shadow-1:0 1px 2px rgba(5,21,51,.06);
  --shadow-2:0 8px 24px rgba(5,21,51,.04);
  --shadow-3:0 24px 64px rgba(5,21,51,.28);
  --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;
}
*,*::before,*::after{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  font-family:var(--sans); background:var(--blanco); color:var(--tinta);
  font-size:14px; line-height:1.6; -webkit-font-smoothing:antialiased;
}
img{max-width:100%;display:block}
a{color:var(--azul-real);text-decoration:none}
a:hover{text-decoration:underline}
:focus-visible{outline:none;box-shadow:0 0 0 3px var(--azul-28);border-radius:var(--r-sm)}
h1,h2,h3,h4{margin:0;font-weight:700;color:var(--tinta);line-height:1.3}
h1{font-size:28px;letter-spacing:-.02em}
h2{font-size:20px;letter-spacing:-.01em}
h3{font-size:16px;font-weight:600;line-height:1.4}
h4{font-size:14px;font-weight:600;line-height:1.4}
p{margin:0}
small{font-size:13px}
.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
"""

# --- Shell: header + sidebar -------------------------------------------------
SHELL_CSS = """
.shell{display:flex;min-height:100vh;background:var(--blanco)}
.sidebar{
  width:264px;flex:0 0 264px;background:var(--azul-noche);
  display:flex;flex-direction:column;position:sticky;top:0;height:100vh;
}
.brand{
  display:flex;flex-direction:column;align-items:center;gap:12px;
  padding:22px 20px 20px;border-bottom:1px solid var(--blanco-08);
}
/* El lockup ya viene recortado a su proporcion real (2.0979:1) y con el fondo
   transparente, asi que la caja solo dimensiona: sin fondo, sin borde y sin
   padding. object-fit:contain evita que un recorte futuro Cutting-edge del PNG
   vuelva a cortar la marca. */
.brand-tile{
  width:180px;flex:0 0 auto;display:block;
}
.brand-tile img{width:100%;height:auto;display:block;object-fit:contain}
.brand-text{text-align:center}
.brand-name{font-size:20px;font-weight:700;color:var(--blanco);line-height:1.15;letter-spacing:.02em}
.brand-sub{font-size:13px;color:var(--blanco);opacity:.82;line-height:1.4;margin-top:4px}
.nav{padding:16px 12px;overflow-y:auto;flex:1}
.nav-group{margin-bottom:18px}
.nav-label{font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--blanco);opacity:.6;padding:0 12px 8px}
.nav a{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:var(--r-sm);color:var(--blanco);opacity:.78;font-size:14px;font-weight:500;margin-bottom:2px}
.nav a:hover{background:var(--blanco-08);opacity:1;text-decoration:none}
.nav a.activo{background:var(--azul-real);opacity:1;font-weight:600}
.nav a svg{flex:0 0 18px}
.side-foot{padding:16px;border-top:1px solid var(--blanco-08)}
.side-card{background:var(--blanco-08);border-radius:var(--r-sm);padding:12px}
.side-card b{display:block;color:var(--blanco);font-size:13px;margin-bottom:2px}
.side-card span{color:var(--blanco);opacity:.8;font-size:13px}
.main{flex:1;min-width:0;display:flex;flex-direction:column}
.topbar{
  height:72px;flex:0 0 72px;background:var(--azul-noche);color:var(--blanco);
  display:flex;align-items:center;gap:16px;padding:0 24px;position:sticky;top:0;z-index:30;
}
.burger{display:none;background:transparent;border:1px solid var(--blanco-08);border-radius:var(--r-sm);color:var(--blanco);width:38px;height:38px;align-items:center;justify-content:center;cursor:pointer}
/* Respaldo decorativo para <=1023px, donde la sidebar sale de pantalla.
   Se pinta con background (no con un segundo <img>) para que el DOM solo
   tenga una instancia del logo: una sola peticion y un solo ALT. */
.topbar-mark{
  display:none;width:104px;height:50px;flex:0 0 104px;
  background-image:var(--logo-blanco-url);background-repeat:no-repeat;
  background-position:left center;background-size:contain;
}
.search{position:relative;flex:1;max-width:420px}
.search input{width:100%;height:38px;border-radius:var(--r-full);border:1px solid var(--blanco-08);background:var(--blanco-08);color:var(--blanco);padding:0 14px 0 38px;font-family:var(--sans);font-size:14px}
.search input::placeholder{color:var(--blanco);opacity:.7}
.search svg{position:absolute;left:13px;top:50%;transform:translateY(-50%);opacity:.85}
.topbar-right{margin-left:auto;display:flex;align-items:center;gap:14px}
.icon-btn{position:relative;width:38px;height:38px;border-radius:var(--r-sm);border:1px solid var(--blanco-08);background:var(--blanco-08);color:var(--blanco);display:flex;align-items:center;justify-content:center;cursor:pointer}
.count{position:absolute;top:-5px;right:-5px;min-width:18px;height:18px;padding:0 4px;border-radius:var(--r-full);background:var(--amarillo);color:var(--tinta);font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;border:1px solid var(--azul-noche)}
.who{display:flex;align-items:center;gap:10px;padding-left:14px;border-left:1px solid var(--blanco-08)}
.avatar{width:36px;height:36px;border-radius:var(--r-full);background:var(--azul-real);color:var(--blanco);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;flex:0 0 36px}
.who-name{font-size:14px;font-weight:600;line-height:1.2;color:var(--blanco)}
.who-role{font-size:13px;font-weight:600;letter-spacing:.06em;color:var(--tinta);background:var(--amarillo);border-radius:var(--r-full);padding:1px 8px;display:inline-block;margin-top:2px}
.content{padding:28px 32px 48px;max-width:1440px;width:100%}
.page-head{display:flex;align-items:flex-start;gap:16px;margin-bottom:24px}
.page-head .sub{color:var(--tinta-2);font-size:14px;margin-top:4px}
.page-head .acciones{margin-left:auto;display:flex;gap:10px;flex-wrap:wrap}
.crumbs{font-size:13px;color:var(--tinta-2);margin-bottom:10px}
.crumbs a{color:var(--tinta-2)}
@media (max-width:1279px){.sidebar{width:72px;flex:0 0 72px}.brand{padding:16px 8px}.brand-tile{width:44px}.brand-text,.nav a span,.nav-label,.side-foot{display:none}.nav a{justify-content:center}}
@media (max-width:1023px){.sidebar{position:fixed;left:0;top:0;z-index:60;transform:translateX(-100%);transition:transform .25s}.sidebar.abierto{transform:translateX(0)}.brand{padding:22px 20px 20px}.brand-tile{width:180px}.brand-text,.nav a span,.nav-label,.side-foot{display:block}.nav a{justify-content:flex-start}.burger{display:flex}.content{padding:20px 16px 40px}.topbar-mark{display:flex}}
/* Con el drawer abierto el logo del drawer tiene el protagonismo: se oculta el
   del topbar para que nunca haya dos logos visibles a la vez. */
.shell:has(.sidebar.abierto) .topbar-mark{display:none}
/* En movil el bloque de identidad (nombre + badge de rol) no cabe junto al
   buscador y los tres botones, y empujaba la barra 102px fuera de pantalla.
   Se conserva el avatar, que ya identifica al usuario, y se retiran los textos. */
@media (max-width:767px){.content{padding:16px 12px 36px}.page-head{flex-direction:column}.page-head .acciones{margin-left:0}.topbar{padding:0 12px;gap:10px}.topbar-right{gap:8px}.who{padding-left:10px;border-left:0}.who-name,.who-role{display:none}.search input{font-size:13px}}
@media (max-width:479px){.search{display:none}}
.overlay{display:none;position:fixed;inset:0;background:var(--noche-55);z-index:55}
.overlay.visible{display:block}
"""

# --- Componentes -------------------------------------------------------------
COMPONENTES_CSS = """
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:40px;padding:0 18px;border-radius:var(--r-sm);border:1px solid transparent;font-family:var(--sans);font-size:14px;font-weight:600;cursor:pointer;white-space:nowrap}
.btn-primario{background:var(--azul-real);color:var(--blanco)}
.btn-primario:hover{background:var(--azul-profundo)}
.btn-acento{background:var(--amarillo);color:var(--tinta)}
.btn-acento:hover{background:var(--azul-profundo);color:var(--blanco)}
.btn-secundario{background:var(--blanco);border-color:var(--gris);color:var(--tinta)}
.btn-secundario:hover{border-color:var(--azul-real);color:var(--azul-real)}
.btn-peligro{background:var(--tinta);color:var(--blanco)}
.btn-peligro:hover{background:var(--azul-profundo)}
.btn-sm{height:32px;padding:0 12px;font-size:13px}
.btn:disabled{background:var(--gris);color:var(--blanco);border-color:var(--gris);cursor:not-allowed}

.card{background:var(--blanco);border:1px solid var(--gris);border-radius:var(--r-md);box-shadow:var(--shadow-1)}
.card-head{display:flex;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid var(--gris)}
.card-head h3{flex:1;font-size:16px;font-weight:600;line-height:1.4;letter-spacing:-.005em}
.card-head .hint{font-size:13px;color:var(--tinta-2);font-weight:400}
.card-body{padding:20px}
.card-body.sin-pad{padding:0}

/* La columna por defecto es minmax(0,1fr) y no auto: una columna auto se mide
   por el max-content de sus hijos, asi que un titulo largo o un <input> con un
   placeholder estiraba la columna a 388px dentro de 351px disponibles en movil.
   minmax(0,1fr) ancla la columna al contenedor y deja que el contenido encoja. */
.grid{display:grid;gap:20px;grid-template-columns:minmax(0,1fr)}
.g-4{grid-template-columns:repeat(4,minmax(0,1fr))}
.g-3{grid-template-columns:repeat(3,minmax(0,1fr))}
.g-2{grid-template-columns:repeat(2,minmax(0,1fr))}
.g-2-1{grid-template-columns:minmax(0,2fr) minmax(0,1fr)}
.g-1-2{grid-template-columns:minmax(0,1fr) minmax(0,2fr)}
/* Filas de botones. Dos botones de ancho fijo suman mas de 375px y la fila no
   tiene una clase comun en el markup, asi que se localizan por su estructura
   y se les deja envolver en vez de salirse de la pantalla. */
@media (max-width:767px){div:has(> .btn + .btn){flex-wrap:wrap}}
@media (max-width:479px){div:has(> .btn + .btn) > .btn{flex:1 1 140px}}
@media (max-width:1279px){.g-4{grid-template-columns:repeat(2,1fr)}}
@media (max-width:1023px){.g-3,.g-2-1,.g-1-2{grid-template-columns:1fr}}
@media (max-width:767px){.g-4,.g-3,.g-2{grid-template-columns:1fr}}

.metrica{padding:20px}
.metrica-top{display:flex;align-items:flex-start;gap:12px;margin-bottom:14px}
.metrica-ico{width:38px;height:38px;flex:0 0 38px;border-radius:var(--r-sm);background:var(--azul-08);color:var(--azul-real);display:flex;align-items:center;justify-content:center}
.metrica-lbl{font-size:13px;color:var(--tinta-2);font-weight:500}
.metrica-val{font-size:32px;font-weight:800;color:var(--tinta);line-height:1.4;letter-spacing:-.02em}
.metrica-val .u{font-size:16px;font-weight:600;color:var(--tinta-2);margin-left:4px}
.metrica-delta{margin-left:auto;font-size:13px;font-weight:600;color:var(--azul-real);display:flex;align-items:center;gap:3px}
.barra{height:6px;background:var(--azul-15);border-radius:var(--r-full);overflow:hidden;margin-top:12px}
.barra span{display:block;height:100%;background:var(--azul-real);border-radius:var(--r-full)}
.barra.amarilla span{background:var(--amarillo)}

table.tabla{width:100%;border-collapse:collapse;font-size:14px}
table.tabla thead th{
  background:var(--azul-profundo);color:var(--blanco);font-size:13px;font-weight:600;
  text-transform:uppercase;letter-spacing:.05em;text-align:left;padding:12px 16px;
  position:sticky;top:0;z-index:2;
}
table.tabla thead th.acc{white-space:nowrap}
table.tabla tbody td{padding:12px 16px;border-bottom:1px solid var(--gris);vertical-align:middle;color:var(--tinta)}
table.tabla tbody tr:nth-child(even){background:var(--noche-03)}
table.tabla tbody tr:hover{background:var(--azul-06)}
table.tabla .num{text-align:right;font-variant-numeric:tabular-nums}
table.tabla .acc{text-align:right;white-space:nowrap}
table.tabla .acc button,.table-act{display:inline-flex;width:32px;height:32px;align-items:center;justify-content:center;border:1px solid var(--gris);background:var(--blanco);border-radius:var(--r-sm);color:var(--azul-real);cursor:pointer;margin-left:4px}
table.tabla .acc button:hover{background:var(--azul-real);color:var(--blanco);border-color:var(--azul-real)}
table.tabla tbody tr:last-child td{border-bottom:none}
.tabla-scroll{overflow-x:auto}
.tabla-envoltura{overflow:hidden}

/* La tabla de administracion tiene 9 columnas. A 16px de padding horizontal por
   celda se pasa del ancho disponible y obliga a desplazar en horizontal, asi que
   por debajo de 1280px el padding lateral se reduce. */
@media (max-width:1279px){
  table.tabla thead th,table.tabla tbody td{padding-left:10px;padding-right:10px}
}

/* Vista tarjeta. A 375px una tabla de hasta 9 columnas no cabe ni con scroll
   horizontal: el dato queda fuera de pantalla y el usuario no lo ve. Se apila
   una fila por tarjeta y cada celda imprime su cabecera con attr(data-label),
   que lib_ui.tabla() escribe en cada celda del cuerpo. */
@media (max-width:767px){
  .tabla-envoltura{background:var(--blanco);border:0;box-shadow:none;padding:0;overflow:visible}
  .tabla-scroll{overflow-x:visible}
  table.tabla{display:block;width:100%}
  table.tabla thead{display:none}
  table.tabla tbody{display:block}
  table.tabla tbody tr{display:block;background:var(--blanco);
    border:1px solid var(--gris);border-radius:var(--r-md);
    box-shadow:var(--shadow-1);margin-bottom:12px;overflow:hidden}
  table.tabla tbody tr:nth-child(even),table.tabla tbody tr:hover{background:var(--blanco)}
  table.tabla tbody tr:last-child{margin-bottom:0}
  table.tabla tbody td{display:flex;align-items:flex-start;gap:12px;width:100%;
    padding:10px 14px;border-bottom:1px solid var(--gris);text-align:left;
    white-space:normal;overflow-wrap:anywhere}
  table.tabla tbody td::before{content:attr(data-label);flex:0 0 38%;
    font-size:13px;font-weight:600;color:var(--azul-real);line-height:1.4;
    text-transform:uppercase;letter-spacing:.04em}
  table.tabla tbody td.acc{justify-content:flex-start}
  table.tabla tbody td.sel{display:none}
  table.tabla tbody tr td:last-child{border-bottom:none}
}
.toolbar{display:flex;align-items:center;gap:12px;padding:14px 16px;border-bottom:1px solid var(--gris);background:var(--blanco);flex-wrap:wrap}
.toolbar .crece{flex:1;min-width:200px}
.buscador{position:relative}
.buscador input{width:100%;height:40px;border:1px solid var(--gris);border-radius:var(--r-sm);padding:0 12px 0 36px;font-family:var(--sans);font-size:14px;color:var(--tinta);background:var(--blanco)}
.buscador input::placeholder{color:var(--gris)}
.buscador svg{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--azul-real)}
select.filtro,input.filtro{height:40px;border:1px solid var(--gris);border-radius:var(--r-sm);padding:0 12px;font-family:var(--sans);font-size:14px;color:var(--tinta);background:var(--blanco)}
.paginacion{display:flex;align-items:center;gap:12px;padding:14px 16px;border-top:1px solid var(--gris);font-size:13px;color:var(--tinta-2);flex-wrap:wrap}
.paginacion .pag{margin-left:auto;display:flex;gap:6px}

.badge{display:inline-flex;align-items:center;gap:5px;padding:3px 11px;border-radius:var(--r-full);font-size:13px;font-weight:600;border:1px solid;white-space:nowrap}
.b-amarillo{background:var(--amarillo-14);color:var(--tinta);border-color:var(--amarillo)}
.b-azul{background:var(--azul-real);color:var(--blanco);border-color:var(--azul-real)}
.b-linea{background:var(--blanco);color:var(--azul-real);border-color:var(--azul-real)}
.b-neutra{background:var(--noche-04);color:var(--tinta-2);border-color:var(--gris)}

.campo{margin-bottom:18px}
.campo label{display:block;font-size:13px;font-weight:600;color:var(--tinta);margin-bottom:6px}
.campo label .req{color:var(--azul-real);margin-left:3px}
.campo input[type=text],.campo input[type=email],.campo input[type=password],.campo input[type=tel],.campo input[type=date],.campo input[type=time],.campo select,.campo textarea{
  width:100%;height:40px;border:1px solid var(--gris);border-radius:var(--r-sm);padding:0 12px;
  font-family:var(--sans);font-size:14px;color:var(--tinta);background:var(--blanco);
}
.campo textarea{height:auto;min-height:104px;padding:10px 12px;resize:vertical;line-height:1.6}
.campo input:focus,.campo select:focus,.campo textarea:focus{border-color:var(--azul-real);box-shadow:0 0 0 3px var(--azul-12);outline:none}
.campo input::placeholder,.campo textarea::placeholder{color:var(--gris)}
.campo input:disabled,.campo select:disabled,.campo textarea:disabled{background:var(--noche-03);color:var(--gris);cursor:not-allowed}
.campo .ayuda{font-size:13px;color:var(--tinta-2);margin-top:5px;display:flex;align-items:flex-start;gap:5px}
.campo .bloqueo{font-size:13px;color:var(--tinta-2);margin-top:5px;display:flex;align-items:center;gap:5px;background:var(--noche-03);border:1px dashed var(--gris);border-radius:var(--r-sm);padding:6px 10px}
.otp{display:flex;gap:10px;flex-wrap:wrap}
.otp span,.otp input{width:52px;height:60px;border:1px solid var(--gris);border-radius:var(--r-sm);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;color:var(--tinta);background:var(--blanco)}
/* Los ocho digitos son campos de verdad: se escriben, se borran y el foco
   salta al siguiente. .otp input toma el ancho de la caja y el texto centrado. */
.otp input{width:52px;padding:0;text-align:center;font-family:var(--sans);font-weight:700}
.otp input:focus{outline:2px solid var(--azul-real);outline-offset:1px;border-color:var(--azul-real)}
@media (max-width:479px){
  .otp{gap:6px}
  .otp input,.otp span{width:calc((100% - 42px)/8);min-width:32px;height:48px;font-size:18px}
}
.drop{border:1px dashed var(--gris);border-radius:var(--r-md);background:var(--noche-02);padding:28px;text-align:center;color:var(--tinta-2)}
.drop svg{color:var(--azul-real);margin:0 auto 8px}
.chk{display:flex;align-items:flex-start;gap:9px;font-size:13px;color:var(--tinta);margin-bottom:14px}
.chk input{margin-top:2px;width:17px;height:17px;accent-color:var(--azul-real);flex:0 0 17px}
.radio-card{border:1px solid var(--gris);border-radius:var(--r-sm);padding:12px 14px;display:flex;gap:10px;align-items:flex-start;cursor:pointer}
.radio-card.sel{border-color:var(--azul-real);background:var(--azul-06);box-shadow:0 0 0 1px var(--azul-real)}
.radio-card input{accent-color:var(--azul-real);margin-top:2px}

.vacio{padding:56px 24px;text-align:center;color:var(--tinta-2)}
.vacio svg{color:var(--gris);margin:0 auto 12px}
.vacio h3{margin-bottom:6px}
.vacio p{font-size:13px;max-width:420px;margin:0 auto 16px}

.steps{display:flex;align-items:center;gap:0;margin-bottom:28px;flex-wrap:wrap}
.step{display:flex;align-items:center;gap:9px}
.step i{width:28px;height:28px;flex:0 0 28px;border-radius:var(--r-full);background:var(--blanco);border:1px solid var(--gris);color:var(--tinta-2);display:flex;align-items:center;justify-content:center;font-style:normal;font-size:13px;font-weight:700}
.step b{font-size:13px;font-weight:500;color:var(--tinta-2)}
.step.activo i{background:var(--azul-real);border-color:var(--azul-real);color:var(--blanco)}
.step.activo b{color:var(--tinta);font-weight:600}
.step.hecho i{background:var(--amarillo);border-color:var(--amarillo);color:var(--tinta)}
.step-line{width:44px;height:1px;background:var(--gris);margin:0 12px}

.lista-def{display:flex;flex-direction:column}
.def-row{display:flex;gap:16px;padding:11px 0;border-bottom:1px solid var(--gris);font-size:14px}
.def-row:last-child{border-bottom:none}
.def-row dt{flex:0 0 210px;color:var(--tinta-2);font-weight:500}
.def-row dd{margin:0;color:var(--tinta);font-weight:500}
/* El dt reserva 210px fijos: a 375px no deja sitio para el valor y la fila se
   sale. En movil el par se apila. */
@media (max-width:767px){.def-row{flex-direction:column;gap:2px}.def-row dt{flex:0 0 auto}}

.tabs{display:flex;gap:4px;border-bottom:1px solid var(--gris);margin-bottom:20px;overflow-x:auto}
.tabs button{background:transparent;border:none;border-bottom:2px solid transparent;padding:10px 14px;font-family:var(--sans);font-size:14px;font-weight:600;color:var(--tinta-2);cursor:pointer;white-space:nowrap}
.tabs button.activo{color:var(--azul-real);border-bottom-color:var(--azul-real)}

.callout{display:flex;gap:12px;padding:14px 16px;border-radius:var(--r-sm);border:1px solid var(--gris);background:var(--noche-03);font-size:13px;color:var(--tinta-2)}
.callout svg{flex:0 0 18px;color:var(--azul-real)}
.callout b{color:var(--tinta)}

.modal-fondo{position:fixed;inset:0;background:var(--noche-55);display:flex;align-items:center;justify-content:center;z-index:70;padding:24px}
.modal{background:var(--blanco);border-radius:var(--r-md);box-shadow:var(--shadow-3);width:100%;max-width:480px;border:1px solid var(--gris)}
.modal.wide{max-width:720px}
.modal-head{display:flex;align-items:center;gap:12px;padding:18px 20px;border-bottom:1px solid var(--gris)}
.modal-head h2{flex:1;font-size:18px}
.modal-body{padding:20px;font-size:14px;color:var(--tinta-2)}
.modal-foot{display:flex;justify-content:flex-end;gap:10px;padding:16px 20px;border-top:1px solid var(--gris)}

.drawer-fondo{position:fixed;inset:0;background:var(--noche-55);z-index:70}
.drawer{position:fixed;top:0;right:0;bottom:0;width:360px;background:var(--blanco);box-shadow:var(--shadow-3);z-index:75;display:flex;flex-direction:column;border-left:1px solid var(--gris)}
.drawer-head{display:flex;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid var(--gris);background:var(--azul-noche)}
.drawer-head h2{flex:1;color:var(--blanco);font-size:16px}
.drawer-body{flex:1;overflow-y:auto}
.notif{display:flex;gap:12px;padding:14px 20px;border-bottom:1px solid var(--gris);background:var(--blanco)}
.notif.no-leida{border-left:3px solid var(--azul-real)}
.notif-dot{width:8px;height:8px;flex:0 0 8px;border-radius:var(--r-full);background:var(--amarillo);margin-top:6px}
.notif h3{font-size:14px;margin-bottom:3px}
.notif p{font-size:13px;color:var(--tinta-2)}
.notif time{font-size:13px;color:var(--gris);display:block;margin-top:5px}

.chip{display:inline-flex;align-items:center;gap:6px;height:28px;padding:0 12px;border-radius:var(--r-full);border:1px solid var(--gris);background:var(--blanco);font-size:13px;font-weight:600;color:var(--tinta-2)}
.chip.on{background:var(--amarillo);border-color:var(--amarillo);color:var(--tinta)}
.chart-titulo{font-size:14px;font-weight:600;color:var(--tinta);margin-bottom:2px}
.chart-sub{font-size:13px;color:var(--tinta-2);margin-bottom:12px}
.leyenda{display:flex;gap:16px;flex-wrap:wrap;margin-top:12px;font-size:13px;color:var(--tinta-2)}
.leyenda i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}
.kpi-inline{display:flex;align-items:baseline;gap:8px}
.kpi-inline b{font-size:24px;font-weight:700;color:var(--tinta)}
.kpi-inline span{font-size:13px;color:var(--tinta-2)}
.divisor{height:1px;background:var(--gris);margin:20px 0}
.nota-foot{font-size:13px;color:var(--tinta-2);margin-top:8px}
"""

# --- Layouts de listado alternativos ------------------------------------------
LISTADOS_CSS = """
.avisos{display:flex;flex-direction:column;gap:20px}
.aviso-grp{background:var(--blanco);border:1px solid var(--gris);border-radius:var(--r-md);box-shadow:var(--shadow-1);overflow:hidden}
.aviso-grp-head{display:flex;align-items:center;gap:10px;padding:13px 20px;background:var(--noche-04);border-bottom:1px solid var(--gris)}
.aviso-grp-titulo{font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--tinta-2)}
.aviso-grp-n{margin-left:auto;font-size:13px;font-weight:700;color:var(--tinta-2);background:var(--blanco);border:1px solid var(--gris);border-radius:var(--r-full);min-width:24px;height:24px;display:flex;align-items:center;justify-content:center;padding:0 8px}
.aviso{display:flex;align-items:flex-start;gap:14px;padding:14px 20px;border-bottom:1px solid var(--gris);border-left:3px solid transparent}
.aviso:last-child{border-bottom:none}
.aviso.u-alta{border-left-color:var(--amarillo);background:var(--amarillo-14)}
.aviso.u-media{border-left-color:var(--azul-real)}
.aviso.u-baja{border-left-color:var(--gris)}
.aviso-ico{width:34px;height:34px;flex:0 0 34px;border-radius:var(--r-sm);background:var(--azul-08);color:var(--azul-real);display:flex;align-items:center;justify-content:center}
.aviso.u-alta .aviso-ico{background:var(--amarillo);color:var(--tinta)}
.aviso-txt{flex:1;min-width:0}
.aviso-titulo{display:block;font-size:14px;font-weight:600;color:var(--tinta);text-decoration:none}
.aviso-titulo:hover{color:var(--azul-real)}
.aviso-meta{font-size:13px;color:var(--tinta-2);margin-top:3px}
.aviso-acc{display:flex;align-items:center;gap:8px;flex:0 0 auto}

.kanban{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;align-items:start}
.kan-col{background:var(--noche-04);border:1px solid var(--gris);border-radius:var(--r-md);padding:16px}
.kan-head{display:flex;align-items:center;gap:10px;margin-bottom:14px}
.kan-titulo{font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--tinta-2)}
.kan-n{margin-left:auto;font-size:13px;font-weight:700;color:var(--tinta-2)}
.kan-card{background:var(--blanco);border:1px solid var(--gris);border-radius:var(--r-sm);padding:14px;margin-bottom:12px;box-shadow:var(--shadow-1)}
.kan-card:last-child{margin-bottom:0}
.kan-card-titulo{font-size:14px;font-weight:600;color:var(--tinta);line-height:1.4}
.kan-meta{font-size:13px;color:var(--tinta-2);margin-top:5px}
.kan-foot{display:flex;align-items:center;gap:8px;margin-top:12px;padding-top:11px;border-top:1px solid var(--gris);font-size:13px;color:var(--tinta-2)}
.kan-empty{font-size:13px;color:var(--gris);text-align:center;padding:18px 0;border:1px dashed var(--gris);border-radius:var(--r-sm)}
@media (max-width:1023px){.kanban{grid-template-columns:1fr}}

.linea{list-style:none;margin:0;padding:0}
.ln-item{display:flex;gap:18px;position:relative;padding-bottom:18px}
.ln-item:last-child{padding-bottom:0}
.ln-item::after{content:"";position:absolute;left:37px;top:56px;bottom:0;width:2px;background:var(--gris)}
.ln-item:last-child::after{display:none}
.ln-fecha{width:76px;flex:0 0 76px;text-align:center;background:var(--blanco);border:1px solid var(--gris);border-radius:var(--r-sm);padding:8px 0;align-self:flex-start}
.ln-fecha b{display:block;font-size:20px;font-weight:800;color:var(--tinta);line-height:1.4}
.ln-fecha span{display:block;font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--tinta-2);margin-top:4px}
.ln-cuerpo{flex:1;min-width:0;border:1px solid var(--gris);border-radius:var(--r-sm);padding:14px 16px;background:var(--blanco)}
.ln-titulo{font-size:14px;font-weight:600;color:var(--tinta)}
.ln-meta{font-size:13px;color:var(--tinta-2);margin-top:4px}

.agenda{display:flex;flex-direction:column;gap:20px}
.ag-dia{background:var(--blanco);border:1px solid var(--gris);border-radius:var(--r-md);box-shadow:var(--shadow-1);overflow:hidden}
.ag-dia-h{display:flex;align-items:baseline;gap:10px;padding:13px 20px;background:var(--azul-profundo);color:var(--blanco)}
.ag-dia-h b{font-size:14px;font-weight:700;letter-spacing:.01em}
.ag-dia-h span{font-size:13px;opacity:.8;margin-left:auto}
.ag-ev{display:flex;align-items:center;gap:16px;padding:14px 20px;border-bottom:1px solid var(--gris)}
.ag-ev:last-child{border-bottom:none}
.ag-hora{width:64px;flex:0 0 64px;font-size:13px;font-weight:700;color:var(--azul-real);font-variant-numeric:tabular-nums}
.ag-txt{flex:1;min-width:0}
.ag-titulo{font-size:14px;font-weight:600;color:var(--tinta)}
.ag-meta{font-size:13px;color:var(--tinta-2);margin-top:3px}

.emp-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
@media (max-width:1279px){.emp-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width:1023px){.emp-grid{grid-template-columns:1fr}}
.emp-card{background:var(--blanco);border:1px solid var(--gris);border-radius:var(--r-md);padding:18px;box-shadow:var(--shadow-1)}
.emp-top{display:flex;align-items:flex-start;gap:12px}
.emp-ico{width:38px;height:38px;flex:0 0 38px;border-radius:var(--r-sm);background:var(--azul-08);color:var(--azul-real);display:flex;align-items:center;justify-content:center}
.emp-txt{min-width:0}
.emp-titulo{font-size:14px;font-weight:600;color:var(--tinta);line-height:1.3}
.emp-meta{font-size:13px;color:var(--tinta-2);margin-top:3px}
.emp-foot{display:flex;align-items:center;justify-content:space-between;margin-top:14px;font-size:13px;color:var(--tinta-2)}
.emp-foot b{font-size:14px;font-weight:800;color:var(--tinta)}

.dist{display:flex;flex-direction:column;gap:12px}
.dist-row{display:flex;align-items:center;gap:14px}
.dist-lbl{width:92px;flex:0 0 92px;font-size:13px;font-weight:600;color:var(--tinta-2)}
.dist-bar{flex:1;height:10px;background:var(--azul-08);border-radius:var(--r-full);overflow:hidden}
.dist-bar i{display:block;height:100%;background:var(--azul-real);border-radius:var(--r-full)}
.dist-row:nth-child(1) .dist-bar i{background:var(--azul-real)}
.dist-row:nth-child(2) .dist-bar i{background:var(--azul-profundo)}
.dist-row:nth-child(3) .dist-bar i{background:var(--azul-real)}
.dist-row:nth-child(4) .dist-bar i{background:var(--amarillo)}
.dist-val{width:44px;flex:0 0 44px;text-align:right;font-size:13px;font-weight:700;color:var(--tinta);font-variant-numeric:tabular-nums}

.fila-simple{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:12px 14px;border:1px solid var(--gris);border-radius:var(--r-sm);background:var(--blanco)}
.fila-simple b{font-size:14px;font-weight:600;color:var(--tinta)}
.fila-simple button{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border:1px solid var(--gris);background:var(--blanco);border-radius:var(--r-sm);color:var(--tinta-2);cursor:pointer}
.fila-simple button:hover{border-color:var(--azul-real);color:var(--azul-real)}
@media (max-width:767px){.fila-simple{flex-wrap:wrap}}

@media (max-width:767px){.aviso{flex-wrap:wrap}.aviso-acc{width:100%;justify-content:flex-end}.ln-item{gap:12px}.ln-fecha{width:62px;flex:0 0 62px}}
"""

# El respaldo del topbar reutiliza el mismo artwork, pero como fondo decorativo.
# Se declara al final y SIN tocar `display`, para que la regla @media de SHELL_CSS
# siga mandando sobre cuando se muestra.
# Aqui va SOLO la variante monocroma: esta entra en las 50 pantallas. La variante
# a color pesa bastante mas y unica hace falta en la barra compacta de las 4
# pantallas de acceso, asi que se declara alla y no aqui (ver LOGO_COLOR_CSS).
TOKENS_LOGO_CSS = ':root{--logo-blanco-url:url("' + LOGO_BLANCO + '")}'

# Se agrega unicamente al <style> de las pantallas de acceso.
LOGO_COLOR_CSS = ':root{--logo-color-url:url("' + LOGO_COLOR + '")}'

# Componentes que crea lib_js.js en tiempo de ejecucion: toasts, modal, drawer de
# notificaciones, menu de usuario, errores de campo y los estados de kanban. Se
# declaran aqui y no en el JS para que el estilo siga siendo revisable y quede
# en el <style> de cada pantalla (Stitch no resuelve hojas externas).
INTERACCION_CSS = (
    "body.sin-scroll{overflow:hidden}"
    ".toast-pila{position:fixed;right:16px;bottom:16px;z-index:120;display:flex;"
    "flex-direction:column;gap:10px;max-width:calc(100vw - 32px)}"
    ".toast{display:flex;align-items:flex-start;gap:10px;padding:12px 16px;border-radius:var(--r-md);"
    "background:var(--azul-noche);color:var(--blanco);font-size:13px;font-weight:500;"
    "box-shadow:var(--shadow-3);animation:toast-in .22s ease-out}"
    ".toast svg{flex:0 0 16px;margin-top:1px}"
    ".toast.t-ok{background:var(--azul-real);box-shadow:var(--shadow-3),inset 4px 0 0 var(--amarillo)}"
    ".toast.t-error{background:var(--azul-noche);box-shadow:var(--shadow-3),inset 4px 0 0 var(--gris)}"
    ".toast.va-fuera{opacity:0;transform:translateY(8px);transition:.4s}"
    "@keyframes toast-in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
    ".modal-velo{position:fixed;inset:0;z-index:110;background:rgba(5,21,51,.55);"
    "display:flex;align-items:center;justify-content:center;padding:20px}"
    ".modal{background:var(--blanco);border-radius:var(--r-md);box-shadow:var(--shadow-3);"
    "width:100%;max-width:520px;max-height:calc(100vh - 40px);display:flex;flex-direction:column}"
    ".modal-head{display:flex;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid var(--gris)}"
    ".modal-head h2{flex:1;font-size:18px;font-weight:700;letter-spacing:-.01em}"
    ".modal-cuerpo{padding:20px;overflow-y:auto}"
    ".modal-foot{display:flex;justify-content:flex-end;gap:10px;padding:14px 20px;border-top:1px solid var(--gris)}"
    ".confirm-texto{font-size:14px;line-height:1.6;color:var(--tinta)}"
    ".modal-aviso{margin-top:12px;font-size:13px;color:var(--tinta-2);line-height:1.6}"
    ".sg-drawer{position:fixed;top:0;right:0;bottom:0;width:min(360px,100vw);z-index:115;"
    "background:var(--blanco);box-shadow:var(--shadow-3);display:flex;flex-direction:column;"
    "animation:drawer-in .22s ease-out}"
    "@keyframes drawer-in{from{transform:translateX(100%)}to{transform:none}}"
    ".sg-drawer-head{display:flex;align-items:center;gap:12px;padding:16px 20px;"
    "background:var(--azul-noche);color:var(--blanco)}"
    ".sg-drawer-head h2{flex:1;font-size:16px;font-weight:700}"
    ".sg-drawer-lista{list-style:none;padding:8px;overflow-y:auto}"
    ".sg-drawer-lista li{display:flex;gap:10px;align-items:flex-start;padding:12px;"
    "border-bottom:1px solid var(--gris);font-size:13px;line-height:1.6;color:var(--tinta)}"
    ".sg-drawer-lista svg{flex:0 0 15px;margin-top:2px;color:var(--azul-real)}"
    ".who-menu{position:absolute;right:0;top:calc(100% + 8px);z-index:60;min-width:200px;"
    "background:var(--blanco);border:1px solid var(--gris);border-radius:var(--r-md);"
    "box-shadow:var(--shadow-3);padding:6px;display:none}"
    ".who-menu.visible{display:block}"
    ".who-menu button{display:block;width:100%;text-align:left;background:none;border:0;"
    "padding:9px 12px;border-radius:var(--r-sm);font-family:var(--sans);font-size:14px;"
    "font-weight:500;color:var(--tinta);cursor:pointer}"
    ".who-menu button:hover{background:var(--azul-06);color:var(--azul-real)}"
    ".topbar-right{position:relative}"
    ".campo-error{display:block;margin-top:4px;font-size:13px;color:var(--tinta);font-weight:700}"
    "[aria-invalid=true]{border-color:var(--azul-real);box-shadow:0 0 0 3px var(--azul-12)}"
    "button.hecho{background:var(--azul-real);border-color:var(--azul-real);color:var(--blanco)}"
    "tr.seleccionada{background:var(--azul-06)}"
    ".kanban-col.sobre{background:var(--azul-06);outline:2px dashed var(--azul-real);outline-offset:-2px}"
    ".k-card.arrastrando{opacity:.45}"
    "@media (prefers-reduced-motion:reduce){.toast,.sg-drawer{animation:none}}"
    "@media (max-width:767px){"
    ".toast-pila{left:12px;right:12px;bottom:12px;max-width:none}"
    ".modal-foot{flex-direction:column-reverse}"
    ".modal-foot .btn{width:100%}"
    "}"
)

LOGO_MARCA_CSS = ""

# Calendario del estudiante. Las celdas se pintaban con 29 style= inline que
# repetian el mismo bloque; la parte que varia (fondo, peso, punto de hito) baja
# a modificadores de clase.
CALENDARIO_CSS = (
    ".cal{display:grid;grid-template-columns:repeat(7,1fr)}"
    ".cal-cab{background:#162644}"
    ".cal-cab div{padding:8px;text-align:center;color:#ffffff;font-size:13px;"
    "font-weight:600;letter-spacing:.04em}"
    ".cal-celda,.cal-vacio{padding:8px;border:1px solid #bbbbbb}"
    ".cal-celda{position:relative;background:#ffffff;color:#051533;"
    "text-align:center;font-size:13px;font-weight:400}"
    ".cal-celda.hoy{background:#ffd300;font-weight:700}"
    ".cal-punto{position:absolute;top:4px;right:4px;width:5px;height:5px;"
    "border-radius:999px;background:#004a93}"
)

CSS = (TOKENS_CSS + TOKENS_LOGO_CSS + SHELL_CSS + COMPONENTES_CSS + LISTADOS_CSS
       + CALENDARIO_CSS + INTERACCION_CSS + LOGO_MARCA_CSS)