package com.jobtracker.service;

import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

@Service
public class S3Service {
    
    private final S3Client s3Client;
    private final String bucketName;
    
    public S3Service(S3Client s3Client, @Value("${s3.bucket.name}") String bucketName) {
        this.s3Client = s3Client;
        this.bucketName = bucketName;
    }
    
    /**
     * Upload resume file to S3
     * @param file Uploaded file
     * @param userId User ID
     * @return S3 object key
     */
    public String uploadResume(MultipartFile file, Long userId) throws IOException {
        // Generate unique filename
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String originalFilename = file.getOriginalFilename();
        String fileExtension = originalFilename != null ? 
            originalFilename.substring(originalFilename.lastIndexOf(".")) : "";
        String fileName = String.format("resumes/user_%d/%s_%s%s", 
            userId, timestamp, UUID.randomUUID().toString().substring(0, 8), fileExtension);
        
        // Upload to S3
        PutObjectRequest putObjectRequest = PutObjectRequest.builder()
            .bucket(bucketName)
            .key(fileName)
            .contentType(file.getContentType())
            .contentLength(file.getSize())
            .build();
        
        s3Client.putObject(putObjectRequest, RequestBody.fromInputStream(file.getInputStream(), file.getSize()));
        
        return fileName;
    }
    
    /**
     * Get presigned URL for S3 file
     * @param objectKey S3 object key
     * @return Presigned URL
     */
    public String getPresignedUrl(String objectKey) {
        GetUrlRequest getUrlRequest = GetUrlRequest.builder()
            .bucket(bucketName)
            .key(objectKey)
            .build();
        
        return s3Client.utilities().getUrl(getUrlRequest).toString();
    }
    
    /**
     * Delete S3 file
     * @param objectKey S3 object key
     */
    public void deleteFile(String objectKey) {
        DeleteObjectRequest deleteObjectRequest = DeleteObjectRequest.builder()
            .bucket(bucketName)
            .key(objectKey)
            .build();
        
        s3Client.deleteObject(deleteObjectRequest);
    }
    
    /**
     * Check if file exists
     * @param objectKey S3 object key
     * @return Whether file exists
     */
    public boolean fileExists(String objectKey) {
        try {
            HeadObjectRequest headObjectRequest = HeadObjectRequest.builder()
                .bucket(bucketName)
                .key(objectKey)
                .build();
            
            s3Client.headObject(headObjectRequest);
            return true;
        } catch (NoSuchKeyException e) {
            return false;
        }
    }
}
