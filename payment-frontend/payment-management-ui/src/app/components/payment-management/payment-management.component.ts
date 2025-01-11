import { Component, OnInit } from '@angular/core';
import { PaymentService } from '../../services/payment.service';
import { Payment } from '../../models/payment.model';
import { FormBuilder, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-payment-management',
  templateUrl: './payment-management.component.html',
  styleUrls: ['./payment-management.component.css'],
})
export class PaymentManagementComponent implements OnInit {
  payments: Payment[] = [];
  searchForm: FormGroup;
  page: number = 1;
  pageSize: number = 10;
  totalItems: number = 0;

  constructor(
    private paymentService: PaymentService,
    private fb: FormBuilder
  ) {
    this.searchForm = this.fb.group({
      search: [''],
      status: [''],
    });
  }

  ngOnInit(): void {
    this.fetchPayments();
  }

  fetchPayments(): void {
    const params = {
      ...this.searchForm.value,
      page: this.page,
      page_size: this.pageSize,
    };

    this.paymentService.getPayments(params).subscribe(
      (response) => {
        this.payments = response.data;
        this.totalItems = response.total;
      },
      (error) => {
        console.error('Error fetching payments:', error);
      }
    );
  }

  onPageChange(page: number): void {
    this.page = page;
    this.fetchPayments();
  }
}
