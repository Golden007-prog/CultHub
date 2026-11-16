import { ArrowRight } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import BackLink from '@/components/common/BackLink'
import Field from '@/components/common/Field'
import Surface from '@/components/common/Surface'
import { Button } from '@/components/ui/button'
import { useDocumentTitle } from '@/hooks/useDocumentTitle'
import { onFormSubmit, text } from '@/lib/forms'
import { paths } from '@/lib/paths'
import { api, ApiError } from '@/services/api'

export default function ResetPassword() {
  useDocumentTitle('Criar nova senha | CultHub')
  const { uid, token } = useParams()
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  return (
    <>
      <BackLink to={paths.signIn}>Voltar para entrar</BackLink>
      <Surface as="section" aria-labelledby="nova-senha-titulo" className="mx-auto mt-8 max-w-lg p-7">
        <h1 id="nova-senha-titulo" className="text-2xl">
          Crie uma nova senha
        </h1>
        <p className="my-3 text-sm text-muted-foreground">Escolha uma senha com pelo menos 8 caracteres.</p>
        <form
          onSubmit={onFormSubmit(async (data) => {
            const password = text(data, 'senha')
            if (password !== text(data, 'confirmar-senha')) {
              setError('As senhas não conferem.')
              return
            }
            if (!uid || !token) {
              setError('Este link de recuperação é inválido ou está incompleto.')
              return
            }
            setSubmitting(true)
            setError('')
            try {
              await api.auth.resetPassword({ uid, token, password })
              navigate(paths.signIn, { replace: true, state: { passwordReset: true } })
            } catch (cause) {
              setError(
                cause instanceof ApiError
                  ? cause.message
                  : 'Não foi possível redefinir a senha. Tente novamente.',
              )
            } finally {
              setSubmitting(false)
            }
          })}
        >
          <Field
            id="nova-senha"
            required
            minLength={8}
            name="senha"
            label="Nova senha"
            type="password"
            autoComplete="new-password"
          />
          <Field
            id="confirmar-senha"
            required
            minLength={8}
            name="confirmar-senha"
            label="Confirme a nova senha"
            type="password"
            autoComplete="new-password"
          />
          {error && (
            <p role="alert" aria-live="polite" className="mb-4 text-sm text-destructive">
              {error}
            </p>
          )}
          <Button type="submit" block disabled={submitting}>
            Salvar nova senha <ArrowRight />
          </Button>
        </form>
        <p className="mt-5 text-sm text-muted-foreground">
          Link expirado?{' '}
          <Link className="text-maroon underline" to={paths.recoverPassword}>
            Solicite outro
          </Link>
        </p>
      </Surface>
    </>
  )
}
