import { Link } from 'react-router-dom';
import { roleKeyOf } from '../../api/types.ts';
import { useAuth } from '../../auth/AuthProvider.tsx';
import { Badge } from '../../components/Badge.tsx';
import { Card } from '../../components/Card.tsx';
import { Callout, DefinitionList } from '../../components/DefinitionList.tsx';
import { PageHeader } from '../../components/PageHeader.tsx';
import { PROFILE_BY_ROLE, ROLE_LABEL } from '../../navigation/nav.ts';

/**
 * Configuración de la cuenta para estudiante y docente.
 *
 * El prototipo ofrecía interruptores de preferencias, pero la API no guarda
 * preferencias por usuario: los avisos son claves globales de
 * `configuracion_programa` (`notif_tareas`, `notif_asesorias`,
 * `notif_seguimiento`) que administra la coordinación (P-31). La vista lo dice
 * en vez de pintar controles que no guardarían nada.
 */
export function AccountSettingsPage() {
  const { user } = useAuth();
  const role = roleKeyOf(user);
  if (!user || !role) return null;

  return (
    <>
      <PageHeader
        title="Configuración"
        sub="Datos de tu cuenta, seguridad y avisos del programa."
        crumbs={[{ label: ROLE_LABEL[role] }, { label: 'Configuración' }]}
      />

      <div className="grid g-2">
        <Card title="Datos personales y académicos" hint="Los editas tú">
          <p className="ayuda" style={{ marginTop: 0 }}>
            Nombres, apellidos, nivel académico, programa, centro universitario, municipio,
            tipo de población y tipo de usuario se editan desde tu perfil. El correo, el
            documento, el rol y el estado los cambia la coordinación del programa.
          </p>
          <Link className="btn btn-primario" to={PROFILE_BY_ROLE[role]}>
            Ir a mi perfil
          </Link>
        </Card>

        <Card title="Seguridad" hint="Código al correo">
          <p className="ayuda" style={{ marginTop: 0 }}>
            No existe un cambio de contraseña autenticado: se envía un código de 8 dígitos
            al correo de tu sesión y se fija la nueva contraseña en el flujo de
            recuperación.
          </p>
          <Link className="btn btn-secundario" to={`/${role}/contrasena`}>
            Cambiar mi contraseña
          </Link>
        </Card>

        <Card title="Avisos del programa" hint="Preferencias globales">
          <DefinitionList
            items={[
              {
                term: 'Tareas',
                value: (
                  <span>
                    <Badge state="Activa">Activo</Badge> clave <code>notif_tareas</code>
                  </span>
                ),
              },
              {
                term: 'Asesorías',
                value: (
                  <span>
                    <Badge state="Activa">Activo</Badge> clave <code>notif_asesorias</code>
                  </span>
                ),
              },
              {
                term: 'Seguimiento',
                value: (
                  <span>
                    <Badge state="Activa">Activo</Badge> clave <code>notif_seguimiento</code>
                  </span>
                ),
              },
            ]}
          />
          <Callout icon="bombilla">
            Estas tres claves las administra la coordinación para todo el programa; no hay
            un interruptor por usuario (P-31). Puedes consultar todos los avisos en tu
            bandeja de notificaciones.
          </Callout>
          <Link className="btn btn-secundario mt-14" to={`/${role}/notificaciones`}>
            Ver mis notificaciones
          </Link>
        </Card>

        <Card title="Cuenta" hint="Solo lectura">
          <DefinitionList
            items={[
              { term: 'Código', value: user.codigo },
              { term: 'Correo institucional', value: user.correoInstitucional },
              { term: 'Rol', value: user.rol.nombre },
              { term: 'Estado', value: <Badge state={user.estado}>{user.estado}</Badge> },
            ]}
          />
        </Card>
      </div>
    </>
  );
}
