import { ArrowRight } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import BackLink from '@/components/common/BackLink'
import Field from '@/components/common/Field'
import Surface from '@/components/common/Surface'
import { Button } from '@/components/ui/button'
import { useDocumentTitle } from '@/hooks/useDocumentTitle'
import { onFormSubmit, text } from '@/lib/forms'
import { paths } from '@/lib/paths'
import { api, ApiError } from '@/services/api'

export default function RecoverPassword() {
  useDocumentTitle('Recuperar senha | CultHub')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  return (
    <>
      <BackLink to={paths.signIn}>Voltar para entrar</BackLink>
      <Surface
        as="section"
        aria-labelledby="recuperar-titulo"
        padded={false}
        className="mx-auto mt-8 max-w-lg p-7"
      >
        <h1 id="recuperar-titulo" className="text-2xl">
          Esqueceu sua senha?
        </h1>
        <p className="my-3 text-sm text-muted-foreground">
          Informe o e-mail da sua conta. Se ele estiver cadastrado, enviaremos um link para criar uma nova
          senha.
        </p>
        <form
          onSubmit={onFormSubmit(async (data) => {
            setSubmitting(true)
            setError('')
            setMessage('')
            try {
              const response = await api.auth.requestPasswordReset(text(data, 'email'))
              setMessage(response.detail)
            } catch (cause) {
              setError(
                cause instanceof ApiError
                  ? cause.message
                  : 'Não foi possível solicitar a recuperação. Tente novamente.',
              )
            } finally {
              setSubmitting(false)
            }
          })}
        >
          <Field
            id="recuperar-email"
            required
            name="email"
            label="E-mail"
            type="email"
            autoComplete="email"
          />
          <Button type="submit" block disabled={submitting}>
            Enviar link <ArrowRight />
          </Button>
        </form>
        {error && (
          <p role="alert" aria-live="polite" className="mt-4 text-sm text-muted-foreground">
            {error}
          </p>
        )}
        {message && (
          <output aria-live="polite" className="mt-4 block text-sm text-muted-foreground">
            {message}
          </output>
        )}
        <p className="mt-5 text-sm text-muted-foreground">
          Lembrou a senha?{' '}
          <Link className="text-maroon underline" to={paths.signIn}>
            Entrar
          </Link>
        </p>
      </Surface>
    </>
  )
}
