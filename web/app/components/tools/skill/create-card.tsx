'use client'
import type { SkillProvider } from '@/service/use-tools'
import {
  RiAddCircleFill,
  RiArrowRightUpLine,
  RiBookOpenLine,
} from '@remixicon/react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useAppContext } from '@/context/app-context'
import SkillModal from './modal'

const SKILL_DOCS_URL = 'https://agentskills.io'

type Props = {
  handleCreate: (provider: SkillProvider) => void
}

const NewSkillCard = ({ handleCreate }: Props) => {
  const { t } = useTranslation()
  const { isCurrentWorkspaceManager } = useAppContext()

  const [showModal, setShowModal] = useState(false)

  return (
    <>
      {isCurrentWorkspaceManager && (
        <div className="col-span-1 flex min-h-[108px] cursor-pointer flex-col rounded-xl bg-background-default-dimmed transition-all duration-200 ease-in-out">
          <div className="group grow rounded-t-xl" onClick={() => setShowModal(true)}>
            <div className="flex shrink-0 items-center p-4 pb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-dashed border-divider-deep group-hover:border-solid group-hover:border-state-accent-hover-alt group-hover:bg-state-accent-hover">
                <RiAddCircleFill className="h-4 w-4 text-text-quaternary group-hover:text-text-accent" />
              </div>
              <div className="system-md-semibold ml-3 text-text-secondary group-hover:text-text-accent">{t('tools.skill.create.cardTitle')}</div>
            </div>
          </div>
          <div className="rounded-b-xl border-t-[0.5px] border-divider-subtle px-4 py-3 text-text-tertiary hover:text-text-accent">
            <a href={SKILL_DOCS_URL} target="_blank" rel="noopener noreferrer" className="flex items-center space-x-1">
              <RiBookOpenLine className="h-3 w-3 shrink-0" />
              <div className="system-xs-regular grow truncate" title={t('tools.skill.create.cardLink') || ''}>{t('tools.skill.create.cardLink')}</div>
              <RiArrowRightUpLine className="h-3 w-3 shrink-0" />
            </a>
          </div>
        </div>
      )}
      {showModal && (
        <SkillModal
          show={showModal}
          onConfirm={handleCreate}
          onHide={() => setShowModal(false)}
        />
      )}
    </>
  )
}
export default NewSkillCard
