# Regras de Compliance e LGPD

## Consentimento
- Sempre verificar `consent_status` e `opt_out` antes de enviar mensagens
- Nunca enviar mensagens para contatos com `opt_out = true`
- Registrar opt-in e opt-out como eventos no Supabase

## LGPD
- Não compartilhar dados do paciente com terceiros sem consentimento
- Não armazenar dados sensíveis em logs
- Nunca expor dados médicos em mensagens de texto simples

## Diagnóstico
- A IA NUNCA deve sugerir diagnósticos médicos
- Em caso de dúvida sobre saúde, orientar a consultar um médico
