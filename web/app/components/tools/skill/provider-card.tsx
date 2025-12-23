'use client'
import type { SkillProvider } from '@/service/use-tools'
import { RiCodeSSlashLine, RiHammerFill } from '@remixicon/react'
import { useBoolean } from 'ahooks'
import { useCallback, useState } from 'react'
import { useTranslation } from 'react-i18next'
import AppIcon from '@/app/components/base/app-icon'
import Confirm from '@/app/components/base/confirm'
import Indicator from '@/app/components/header/indicator'
import { useAppContext } from '@/context/app-context'
import { useDeleteSkill, useInvalidateSkillProviders } from '@/service/use-tools'
import { cn } from '@/utils/classnames'
import OperationDropdown from '../mcp/detail/operation-dropdown'

type Props = {
  currentProvider?: SkillProvider
  data: SkillProvider
  handleSelect: (providerID: string) => void
  onDeleted: () => void
}

const SkillCard = ({
  currentProvider,
  data,
  handleSelect,
  onDeleted,
}: Props) => {
  const { t } = useTranslation()
  const { isCurrentWorkspaceManager } = useAppContext()
  const invalidateSkillProviders = useInvalidateSkillProviders()

  const { mutateAsync: deleteSkill } = useDeleteSkill({
    onSuccess: () => {
      invalidateSkillProviders()
    },
  })

  const [isOperationShow, setIsOperationShow] = useState(false)

  const [isShowDeleteConfirm, {
    setTrue: showDeleteConfirm,
    setFalse: hideDeleteConfirm,
  }] = useBoolean(false)

  const [deleting, {
    setTrue: showDeleting,
    setFalse: hideDeleting,
  }] = useBoolean(false)

  const handleDelete = useCallback(async () => {
    showDeleting()
    await deleteSkill(data.id)
    hideDeleting()
    hideDeleteConfirm()
    onDeleted()
  }, [showDeleting, deleteSkill, data.id, hideDeleting, hideDeleteConfirm, onDeleted])

  const icon = typeof data.icon === 'object' ? data.icon : { background: '#6366f1', content: data.icon || '🎯' }

  return (
    <div
      onClick={() => handleSelect(data.id)}
      className={cn(
        'group relative flex cursor-pointer flex-col rounded-xl border-[1.5px] border-transparent bg-components-card-bg shadow-xs hover:bg-components-card-bg-alt hover:shadow-md',
        currentProvider?.id === data.id && 'border-components-option-card-option-selected-border bg-components-card-bg-alt',
      )}
    >
      <div className="flex grow items-center gap-3 rounded-t-xl p-4">
        <div className="shrink-0 overflow-hidden rounded-xl border border-components-panel-border-subtle">
          <AppIcon
            size="large"
            iconType="emoji"
            icon={icon.content}
            background={icon.background}
          />
        </div>
        <div className="grow">
          <div className="system-md-semibold mb-1 truncate text-text-secondary" title={data.name}>{data.name}</div>
          <div className="system-xs-regular text-text-tertiary">{data.skill_identifier}</div>
        </div>
      </div>
      <div className="flex items-center gap-1 rounded-b-xl pb-2.5 pl-4 pr-2.5 pt-1.5">
        <div className="flex w-0 grow items-center gap-2">
          <div className="flex items-center gap-1">
            {data.has_scripts
              ? (
                  <>
                    <RiCodeSSlashLine className="h-3 w-3 shrink-0 text-text-quaternary" />
                    <div className="system-xs-regular shrink-0 text-text-tertiary">{t('tools.skill.hasScripts')}</div>
                  </>
                )
              : (
                  <>
                    <RiHammerFill className="h-3 w-3 shrink-0 text-text-quaternary" />
                    <div className="system-xs-regular shrink-0 text-text-tertiary">{t('tools.skill.noScripts')}</div>
                  </>
                )}
          </div>
          <div className="system-xs-regular text-divider-deep">/</div>
          <div className="system-xs-regular truncate text-text-tertiary" title={`v${data.version}`}>
            v
            {data.version}
          </div>
        </div>
        {data.enabled && <Indicator color="green" className="shrink-0" />}
        {!data.enabled && (
          <div className="system-xs-medium flex shrink-0 items-center gap-1 rounded-md border border-util-colors-gray-gray-500 bg-components-badge-bg-gray-soft px-1.5 py-0.5 text-util-colors-gray-gray-500">
            {t('tools.skill.disabled')}
            <Indicator color="gray" />
          </div>
        )}
      </div>
      {isCurrentWorkspaceManager && (
        <div className={cn('absolute right-2.5 top-2.5 hidden group-hover:block', isOperationShow && 'block')} onClick={e => e.stopPropagation()}>
          <OperationDropdown
            inCard
            onOpenChange={setIsOperationShow}
            onRemove={showDeleteConfirm}
          />
        </div>
      )}
      {isShowDeleteConfirm && (
        <Confirm
          isShow
          title={t('tools.skill.delete')}
          content={(
            <div>
              {t('tools.skill.deleteConfirmTitle', { skill: data.name })}
            </div>
          )}
          onCancel={hideDeleteConfirm}
          onConfirm={handleDelete}
          isLoading={deleting}
          isDisabled={deleting}
        />
      )}
    </div>
  )
}
export default SkillCard
