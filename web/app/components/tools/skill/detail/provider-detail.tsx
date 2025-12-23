'use client'
import type { SkillProvider } from '@/service/use-tools'
import { RiCloseLine } from '@remixicon/react'
import Drawer from '@/app/components/base/drawer'
import SkillDetailContent from './content'

type Props = {
  detail: SkillProvider
  onHide: () => void
}

const SkillDetailPanel = ({
  detail,
  onHide,
}: Props) => {
  return (
    <Drawer
      isOpen
      onClose={onHide}
      panelClassName="!w-[420px]"
      mask={false}
    >
      <div className="flex h-full flex-col">
        <div className="flex shrink-0 items-center justify-between border-b border-divider-subtle p-4">
          <span className="system-xl-semibold text-text-primary">{detail.name}</span>
          <button
            type="button"
            onClick={onHide}
            className="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-components-button-ghost-bg-hover"
          >
            <RiCloseLine className="h-5 w-5 text-text-tertiary" />
          </button>
        </div>
        <SkillDetailContent providerId={detail.id} />
      </div>
    </Drawer>
  )
}
export default SkillDetailPanel
