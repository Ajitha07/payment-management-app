import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Payment } from '../models/payment.model';
import { environment } from '../../environments/environment'; // Import the environment configuration

@Injectable({
  providedIn: 'root',
})
export class PaymentService {
  private apiUrl = environment.apiUrl; // Use the environment configuration for the base URL

  constructor(private http: HttpClient) {}

  getPayments(params: any): Observable<any> {
    return this.http.get(`${this.apiUrl}/get_payments`, { params });
  }

  createPayment(payment: Payment): Observable<any> {
    return this.http.post(`${this.apiUrl}/create_payment`, payment);
  }

  updatePayment(paymentId: string, updates: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/update_payment/${paymentId}`, updates);
  }

  deletePayment(paymentId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/delete_payment/${paymentId}`);
  }

  uploadEvidence(paymentId: string, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/upload_evidence/${paymentId}`, formData);
  }

  downloadEvidence(paymentId: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/download_evidence/${paymentId}`, {
      responseType: 'blob',
    });
  }
}
