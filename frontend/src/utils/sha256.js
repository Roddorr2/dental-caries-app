/**
 * Calcula el hash SHA-256 de un archivo o ArrayBuffer usando la Web Crypto API nativa.
 * El backend dental-app utiliza este hash para deduplicación estricta.
 *
 * @param {File | Blob | ArrayBuffer} fileOrBuffer - Archivo o buffer a calcular
 * @returns {Promise<string>} Hash en formato hexadecimal de 64 caracteres en minúsculas
 */
export async function computeSHA256(fileOrBuffer) {
  let buffer;

  if (fileOrBuffer instanceof ArrayBuffer) {
    buffer = fileOrBuffer;
  } else if (fileOrBuffer instanceof Blob || fileOrBuffer instanceof File) {
    buffer = await fileOrBuffer.arrayBuffer();
  } else {
    throw new TypeError('El parámetro debe ser un File, Blob o ArrayBuffer');
  }

  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
}
