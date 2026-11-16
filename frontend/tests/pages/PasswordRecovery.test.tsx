import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { paths, routes } from '@/lib/paths'
import RecoverPassword from '@/pages/RecoverPassword'
import ResetPassword from '@/pages/ResetPassword'
import { api, ApiError } from '@/services/api'
import { renderWithRouter } from '@tests/render'

function renderReset(route = paths.resetPassword('user-id', 'valid-token')) {
  return renderWithRouter(
    <Routes>
      <Route path={routes.resetPassword} element={<ResetPassword />} />
      <Route path={routes.signIn} element={<p>Entrar novamente</p>} />
      <Route path="*" element={<ResetPassword />} />
    </Routes>,
    { route, authUser: null },
  )
}

describe('recuperação de senha', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('solicita link e mostra a confirmação genérica', async () => {
    const requestReset = vi
      .spyOn(api.auth, 'requestPasswordReset')
      .mockResolvedValue({ detail: 'Se o e-mail estiver cadastrado, enviaremos um link.' })
    const { user } = renderWithRouter(<RecoverPassword />, { authUser: null })

    await user.type(screen.getByLabelText('E-mail'), 'pessoa@exemplo.com')
    await user.click(screen.getByRole('button', { name: 'Enviar link' }))

    expect(requestReset).toHaveBeenCalledWith('pessoa@exemplo.com')
    expect(await screen.findByText('Se o e-mail estiver cadastrado, enviaremos um link.')).toBeVisible()
  })

  it('mostra falha ao solicitar recuperação', async () => {
    vi.spyOn(api.auth, 'requestPasswordReset').mockRejectedValue(
      new ApiError('Tente novamente mais tarde.', 429),
    )
    const { user } = renderWithRouter(<RecoverPassword />, { authUser: null })

    await user.type(screen.getByLabelText('E-mail'), 'pessoa@exemplo.com')
    await user.click(screen.getByRole('button', { name: 'Enviar link' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Tente novamente mais tarde.')
  })

  it('mostra mensagem genérica quando a solicitação falha sem erro da API', async () => {
    vi.spyOn(api.auth, 'requestPasswordReset').mockRejectedValue(new Error('offline'))
    const { user } = renderWithRouter(<RecoverPassword />, { authUser: null })

    await user.type(screen.getByLabelText('E-mail'), 'pessoa@exemplo.com')
    await user.click(screen.getByRole('button', { name: 'Enviar link' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível solicitar a recuperação. Tente novamente.',
    )
  })

  it('não envia a nova senha quando a confirmação não confere', async () => {
    const resetPassword = vi.spyOn(api.auth, 'resetPassword')
    const { user } = renderReset()

    await user.type(screen.getByLabelText('Nova senha'), 'nova-senha-1234')
    await user.type(screen.getByLabelText('Confirme a nova senha'), 'senha-diferente')
    await user.click(screen.getByRole('button', { name: 'Salvar nova senha' }))

    expect(resetPassword).not.toHaveBeenCalled()
    expect(await screen.findByRole('alert')).toHaveTextContent('As senhas não conferem.')
  })

  it('rejeita link sem uid ou token', async () => {
    const resetPassword = vi.spyOn(api.auth, 'resetPassword')
    const { user } = renderReset('/redefinir-senha/')

    await user.type(screen.getByLabelText('Nova senha'), 'nova-senha-1234')
    await user.type(screen.getByLabelText('Confirme a nova senha'), 'nova-senha-1234')
    await user.click(screen.getByRole('button', { name: 'Salvar nova senha' }))

    expect(resetPassword).not.toHaveBeenCalled()
    expect(await screen.findByRole('alert')).toHaveTextContent('link de recuperação é inválido')
  })

  it('envia a nova senha e segue para o login após sucesso', async () => {
    const resetPassword = vi.spyOn(api.auth, 'resetPassword').mockResolvedValue({
      detail: 'Senha redefinida com sucesso.',
    })
    const { user } = renderReset()

    await user.type(screen.getByLabelText('Nova senha'), 'nova-senha-1234')
    await user.type(screen.getByLabelText('Confirme a nova senha'), 'nova-senha-1234')
    await user.click(screen.getByRole('button', { name: 'Salvar nova senha' }))

    expect(resetPassword).toHaveBeenCalledWith({
      uid: 'user-id',
      token: 'valid-token',
      password: 'nova-senha-1234',
    })
    expect(await screen.findByText('Entrar novamente')).toBeVisible()
  })

  it('mostra erro devolvido ao confirmar a nova senha', async () => {
    vi.spyOn(api.auth, 'resetPassword').mockRejectedValue(
      new ApiError('Este link de recuperação é inválido ou expirou.', 400),
    )
    const { user } = renderReset()

    await user.type(screen.getByLabelText('Nova senha'), 'nova-senha-1234')
    await user.type(screen.getByLabelText('Confirme a nova senha'), 'nova-senha-1234')
    await user.click(screen.getByRole('button', { name: 'Salvar nova senha' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Este link de recuperação é inválido ou expirou.',
    )
  })

  it('mostra mensagem genérica se a confirmação falha sem erro da API', async () => {
    vi.spyOn(api.auth, 'resetPassword').mockRejectedValue(new Error('offline'))
    const { user } = renderReset()

    await user.type(screen.getByLabelText('Nova senha'), 'nova-senha-1234')
    await user.type(screen.getByLabelText('Confirme a nova senha'), 'nova-senha-1234')
    await user.click(screen.getByRole('button', { name: 'Salvar nova senha' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível redefinir a senha. Tente novamente.',
    )
  })
})
