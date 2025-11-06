import React, { useRef, useState } from 'react';
import { Upload, X, Image as ImageIcon, Video, File as FileIcon, Loader } from 'lucide-react';

interface MediaUploaderProps {
  onFileSelect: (file: File) => void;
  onClear: () => void;
  isUploading: boolean;
  mediaUrl?: string;
  mediaType?: string;
  mediaFilename?: string;
}

export const MediaUploader: React.FC<MediaUploaderProps> = ({
  onFileSelect,
  onClear,
  isUploading,
  mediaUrl,
  mediaType,
  mediaFilename
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const getMediaIcon = () => {
    if (mediaType === 'photo') return <ImageIcon className="h-8 w-8 text-blue-500" />;
    if (mediaType === 'video') return <Video className="h-8 w-8 text-purple-500" />;
    return <FileIcon className="h-8 w-8 text-gray-500" />;
  };

  if (mediaUrl) {
    return (
      <div className="border-2 border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getMediaIcon()}
            <div>
              <p className="text-sm font-medium text-gray-900">Медиа прикреплено</p>
              {mediaFilename && (
                <p className="text-xs text-gray-500">{mediaFilename}</p>
              )}
            </div>
          </div>
          <button
            onClick={onClear}
            disabled={isUploading}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {mediaType === 'photo' && mediaUrl && (
          <div className="mt-3">
            <img 
              src={mediaUrl} 
              alt="Preview" 
              className="max-h-48 rounded-lg object-contain"
            />
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-6 transition-colors ${
        dragActive 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-300 hover:border-gray-400'
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept="image/*,video/*,.pdf,.doc,.docx"
        onChange={handleChange}
        disabled={isUploading}
      />

      <div className="text-center">
        {isUploading ? (
          <div className="flex flex-col items-center space-y-2">
            <Loader className="h-8 w-8 text-blue-500 animate-spin" />
            <p className="text-sm text-gray-600">Загрузка...</p>
          </div>
        ) : (
          <>
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <div className="mt-3">
              <button
                type="button"
                onClick={handleButtonClick}
                className="text-blue-600 hover:text-blue-500 font-medium"
              >
                Выберите файл
              </button>
              <span className="text-gray-600"> или перетащите сюда</span>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              PNG, JPG, MP4, PDF, DOC до 50MB
            </p>
          </>
        )}
      </div>
    </div>
  );
};
