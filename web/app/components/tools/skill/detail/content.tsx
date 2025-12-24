'use client'
import {
  RiBookOpenLine,
  RiCodeSSlashLine,
  RiGitBranchLine,
  RiLink,
  RiUser3Line,
} from '@remixicon/react'
import { useTranslation } from 'react-i18next'
import AppIcon from '@/app/components/base/app-icon'
import Loading from '@/app/components/base/loading'
import { useSkillProviderDetail } from '@/service/use-tools'

type Props = {
  providerId: string
}

const SkillDetailContent = ({ providerId }: Props) => {
  const { t } = useTranslation()
  const { data: detail, isLoading } = useSkillProviderDetail(providerId)

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loading />
      </div>
    )
  }

  if (!detail)
    return null

  const icon = typeof detail.icon === 'object' ? detail.icon : { background: '#6366f1', content: detail.icon || '🎯' }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {/* Header */}
      <div className="mb-4 flex items-start gap-3">
        <div className="shrink-0 overflow-hidden rounded-xl border border-components-panel-border-subtle">
          <AppIcon
            size="large"
            iconType="emoji"
            icon={icon.content}
            background={icon.background}
          />
        </div>
        <div>
          <h2 className="system-lg-semibold text-text-primary">{detail.name}</h2>
          <p className="system-xs-regular mt-0.5 text-text-tertiary">{detail.skill_identifier}</p>
        </div>
      </div>

      {/* Description */}
      {detail.description && (
        <div className="mb-4">
          <p className="system-sm-regular text-text-secondary">{detail.description}</p>
        </div>
      )}

      {/* Metadata */}
      <div className="mb-4 space-y-2 rounded-lg bg-components-panel-bg p-3">
        <div className="flex items-center gap-2">
          <RiGitBranchLine className="h-4 w-4 shrink-0 text-text-tertiary" />
          <span className="system-xs-regular text-text-tertiary">
            {t('tools.skill.version')}
            :
          </span>
          <span className="system-xs-medium text-text-secondary">
            v
            {detail.version}
          </span>
        </div>
        {detail.author && (
          <div className="flex items-center gap-2">
            <RiUser3Line className="h-4 w-4 shrink-0 text-text-tertiary" />
            <span className="system-xs-regular text-text-tertiary">
              {t('tools.skill.author')}
              :
            </span>
            <span className="system-xs-medium text-text-secondary">{detail.author}</span>
          </div>
        )}
        {detail.source_url && (
          <div className="flex items-center gap-2">
            <RiLink className="h-4 w-4 shrink-0 text-text-tertiary" />
            <span className="system-xs-regular text-text-tertiary">
              {t('tools.skill.source')}
              :
            </span>
            <a
              href={detail.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="system-xs-medium truncate text-text-accent hover:underline"
            >
              {detail.source_url}
            </a>
          </div>
        )}
        {detail.license && (
          <div className="flex items-center gap-2">
            <RiBookOpenLine className="h-4 w-4 shrink-0 text-text-tertiary" />
            <span className="system-xs-regular text-text-tertiary">
              {t('tools.skill.license')}
              :
            </span>
            <span className="system-xs-medium text-text-secondary">{detail.license}</span>
          </div>
        )}
      </div>

      {/* Scripts */}
      {detail.scripts && detail.scripts.length > 0 && (
        <div className="mb-4">
          <h3 className="system-sm-semibold mb-2 flex items-center gap-1 text-text-secondary">
            <RiCodeSSlashLine className="h-4 w-4" />
            {t('tools.skill.scripts')}
            {' '}
            (
            {detail.scripts.length}
            )
          </h3>
          <div className="space-y-2">
            {detail.scripts.map((script, index) => (
              <div
                key={index}
                className="rounded-lg border border-components-panel-border bg-components-panel-bg-blur p-3"
              >
                <div className="system-sm-medium text-text-primary">{script.name}</div>
                {script.description && (
                  <p className="system-xs-regular mt-1 text-text-tertiary">{script.description}</p>
                )}
                <div className="mt-2 flex items-center gap-2">
                  <span className="system-2xs-medium-uppercase rounded bg-components-badge-bg-gray-soft px-1.5 py-0.5 text-text-tertiary">
                    {script.language}
                  </span>
                  <span className="system-xs-regular text-text-quaternary">{script.path}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full Content Preview */}
      {detail.full_content && (
        <div>
          <h3 className="system-sm-semibold mb-2 text-text-secondary">{t('tools.skill.content')}</h3>
          <div className="max-h-[300px] overflow-y-auto rounded-lg border border-components-panel-border bg-components-panel-bg-blur p-3">
            <pre className="system-xs-regular whitespace-pre-wrap text-text-tertiary">
              {detail.full_content}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
export default SkillDetailContent
