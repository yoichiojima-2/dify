'use client'
import type { SkillProvider } from '@/service/use-tools'
import {
  RiGitBranchLine,
  RiGithubFill,
  RiUploadCloud2Line,
} from '@remixicon/react'
import { useCallback, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Button from '@/app/components/base/button'
import Input from '@/app/components/base/input'
import Modal from '@/app/components/base/modal'
import Toast from '@/app/components/base/toast'
import { useInstallSkill, useInvalidateSkillProviders, useUploadSkill } from '@/service/use-tools'
import { cn } from '@/utils/classnames'

type TabType = 'git' | 'upload'

type Props = {
  show: boolean
  onConfirm: (provider: SkillProvider) => void
  onHide: () => void
}

const SkillModal = ({
  show,
  onConfirm,
  onHide,
}: Props) => {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<TabType>('git')
  const [isLoading, setIsLoading] = useState(false)

  // Git form state
  const [gitUrl, setGitUrl] = useState('')
  const [gitBranch, setGitBranch] = useState('main')
  const [name, setName] = useState('')

  // Upload form state
  const [file, setFile] = useState<File | null>(null)

  const { mutateAsync: installSkill } = useInstallSkill()
  const { mutateAsync: uploadSkill } = useUploadSkill()
  const invalidateSkillProviders = useInvalidateSkillProviders()

  const handleSubmit = useCallback(async () => {
    if (activeTab === 'git') {
      if (!gitUrl.trim()) {
        Toast.notify({ type: 'error', message: t('tools.skill.errors.gitUrlRequired') })
        return
      }

      setIsLoading(true)
      try {
        const provider = await installSkill({
          source_type: 'git',
          git_url: gitUrl.trim(),
          git_branch: gitBranch.trim() || 'main',
          name: name.trim() || undefined,
        })
        invalidateSkillProviders()
        Toast.notify({ type: 'success', message: t('tools.skill.installSuccess') })
        onConfirm(provider)
        onHide()
      }
      catch (error: any) {
        Toast.notify({ type: 'error', message: error?.message || t('tools.skill.errors.installFailed') })
      }
      finally {
        setIsLoading(false)
      }
    }
    else if (activeTab === 'upload') {
      if (!file) {
        Toast.notify({ type: 'error', message: t('tools.skill.errors.fileRequired') })
        return
      }

      setIsLoading(true)
      try {
        const provider = await uploadSkill({
          file,
          name: name.trim() || undefined,
        })
        invalidateSkillProviders()
        Toast.notify({ type: 'success', message: t('tools.skill.installSuccess') })
        onConfirm(provider)
        onHide()
      }
      catch (error: any) {
        Toast.notify({ type: 'error', message: error?.message || t('tools.skill.errors.uploadFailed') })
      }
      finally {
        setIsLoading(false)
      }
    }
  }, [activeTab, gitUrl, gitBranch, name, file, installSkill, uploadSkill, invalidateSkillProviders, onConfirm, onHide, t])

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.zip')) {
        Toast.notify({ type: 'error', message: t('tools.skill.errors.invalidFileType') })
        return
      }
      setFile(selectedFile)
    }
  }, [t])

  return (
    <Modal
      isShow={show}
      onClose={onHide}
      className="!max-w-[480px]"
    >
      <div className="p-6">
        <div className="mb-6 text-xl font-semibold text-text-primary">
          {t('tools.skill.create.title')}
        </div>

        {/* Tabs */}
        <div className="mb-4 flex gap-2">
          <button
            type="button"
            onClick={() => setActiveTab('git')}
            className={cn(
              'flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
              activeTab === 'git'
                ? 'bg-components-button-secondary-bg text-text-primary'
                : 'text-text-tertiary hover:bg-components-button-ghost-bg-hover',
            )}
          >
            <RiGithubFill className="h-4 w-4" />
            {t('tools.skill.create.fromGit')}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('upload')}
            className={cn(
              'flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
              activeTab === 'upload'
                ? 'bg-components-button-secondary-bg text-text-primary'
                : 'text-text-tertiary hover:bg-components-button-ghost-bg-hover',
            )}
          >
            <RiUploadCloud2Line className="h-4 w-4" />
            {t('tools.skill.create.fromUpload')}
          </button>
        </div>

        {/* Git Form */}
        {activeTab === 'git' && (
          <div className="space-y-4">
            <div>
              <label className="system-sm-semibold mb-1 block text-text-secondary">
                {t('tools.skill.create.gitUrl')}
                {' '}
                <span className="text-text-destructive">*</span>
              </label>
              <Input
                value={gitUrl}
                onChange={e => setGitUrl(e.target.value)}
                placeholder="https://github.com/org/skill-repo"
              />
            </div>
            <div>
              <label className="system-sm-semibold mb-1 flex items-center gap-1 text-text-secondary">
                <RiGitBranchLine className="h-3.5 w-3.5" />
                {t('tools.skill.create.gitBranch')}
              </label>
              <Input
                value={gitBranch}
                onChange={e => setGitBranch(e.target.value)}
                placeholder="main"
              />
            </div>
            <div>
              <label className="system-sm-semibold mb-1 block text-text-secondary">
                {t('tools.skill.create.displayName')}
              </label>
              <Input
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder={t('tools.skill.create.displayNamePlaceholder') || ''}
              />
              <p className="mt-1 text-xs text-text-tertiary">{t('tools.skill.create.displayNameHint')}</p>
            </div>
          </div>
        )}

        {/* Upload Form */}
        {activeTab === 'upload' && (
          <div className="space-y-4">
            <div>
              <label className="system-sm-semibold mb-1 block text-text-secondary">
                {t('tools.skill.create.uploadFile')}
                {' '}
                <span className="text-text-destructive">*</span>
              </label>
              <div className="relative">
                <input
                  type="file"
                  accept=".zip"
                  onChange={handleFileChange}
                  className="hidden"
                  id="skill-file-upload"
                />
                <label
                  htmlFor="skill-file-upload"
                  className={cn(
                    'flex cursor-pointer items-center justify-center gap-2 rounded-lg border-2 border-dashed px-4 py-8 transition-colors',
                    file
                      ? 'bg-components-button-primary-bg/5 border-components-button-primary-bg'
                      : 'border-divider-regular hover:border-divider-deep hover:bg-components-panel-bg-blur',
                  )}
                >
                  <RiUploadCloud2Line className="h-5 w-5 text-text-tertiary" />
                  <span className="text-sm text-text-secondary">
                    {file ? file.name : t('tools.skill.create.uploadHint')}
                  </span>
                </label>
              </div>
              <p className="mt-1 text-xs text-text-tertiary">{t('tools.skill.create.uploadFormat')}</p>
            </div>
            <div>
              <label className="system-sm-semibold mb-1 block text-text-secondary">
                {t('tools.skill.create.displayName')}
              </label>
              <Input
                value={name}
                onChange={e => setName(e.target.value)}
                placeholder={t('tools.skill.create.displayNamePlaceholder') || ''}
              />
              <p className="mt-1 text-xs text-text-tertiary">{t('tools.skill.create.displayNameHint')}</p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mt-6 flex justify-end gap-2">
          <Button onClick={onHide} disabled={isLoading}>
            {t('common.operation.cancel')}
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={isLoading}
            disabled={isLoading}
          >
            {t('tools.skill.create.install')}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
export default SkillModal
