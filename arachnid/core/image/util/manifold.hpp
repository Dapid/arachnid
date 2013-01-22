typedef long size_type;

#define USE_BLAS
#ifdef USE_BLAS
inline void x_gemm(const enum CBLAS_ORDER order, const enum CBLAS_TRANSPOSE transa, const enum CBLAS_TRANSPOSE transb, const int m, const int n, const int k, const float alpha, const float* A, const int lda, const float* B, const int ldb, const float beta, float* C, const int ldc)
{
	cblas_sgemm(order, transa, transb, m, n, k, alpha, A, lda, B, ldb, beta, C, ldc);
}
inline void x_gemm(const enum CBLAS_ORDER order, const enum CBLAS_TRANSPOSE transa, const enum CBLAS_TRANSPOSE transb, const int m, const int n, const int k, const double alpha, const double* A, const int lda, const double* B, const int ldb, const double beta, double* C, const int ldc)
{
	cblas_dgemm(order, transa, transb, m, n, k, alpha, A, lda, B, ldb, beta, C, ldc);
}

template<class T>
void gemm(T* samp1, int n1, int m1, T* samp2, int n2, int m2, T* distm, int n3, int m3, double alpha, double beta)
{
	x_gemm(CblasRowMajor, CblasNoTrans, CblasTrans, n1, n2, m1, T(alpha), samp1, m1, samp2, m1, T(beta), distm, n2);
}
#endif

template<class I, class T>
I knn_reduce_eps_cmp(T* data, size_type nd, I* col_ind, size_type nc, I* row_ind, size_type nr, T* sdata, size_type snd, I* scol_ind, size_type snc, I* srow_ind, size_type snr, T* cdata, size_type cnd, float eps)
{
	I j=0;
	for(size_type r=0;r<snr;++r)
	{
		//if( r < 20 ) fprintf(stderr, "data[%d]=%f < %f\n", r, data[r], eps);
		if( cdata[r] < eps )
		{
			sdata[j]=data[r];
			scol_ind[j]=col_ind[r];
			srow_ind[j]=row_ind[r];
			++j;
		}
	}
	return j;
}


template<class I, class T>
I knn_reduce_eps(T* data, size_type nd, I* col_ind, size_type nc, I* row_ind, size_type nr, T* sdata, size_type snd, I* scol_ind, size_type snc, I* srow_ind, size_type snr, float eps)
{
	I j=0;
	for(size_type r=0;r<snr;++r)
	{
		//if( r < 20 ) fprintf(stderr, "data[%d]=%f < %f\n", r, data[r], eps);
		if( data[r] < eps )
		{
			sdata[j]=data[r];
			scol_ind[j]=col_ind[r];
			srow_ind[j]=row_ind[r];
			++j;
		}
	}
	return j;
}

template<class I, class T>
void knn_reduce(T* data, size_type nd, I* col_ind, size_type nc, I* row_ind, size_type nr, T* sdata, size_type snd, I* scol_ind, size_type snc, I* srow_ind, size_type snr, int d, int k)
{
	if( snr > 0 )
	{
		sdata[0]=data[0];
		scol_ind[0]=col_ind[0];
		srow_ind[0]=row_ind[0];
	}
	size_type j=1;
	for(size_type r=1;r<snr;++r,++j)
	{
		assert(r<snd);
		if( (r%k)==0 ) j+=size_type(d);
		assert(j<nd);
		sdata[r]=data[j];
		scol_ind[r]=col_ind[j];
		srow_ind[r]=row_ind[j];
	}
	assert(j==nd);
}

template<class I>
I* find_mutual(I* b, I* e, I v)
{
	for(;b < e;++b) if( (*b) == v ) return b;
	return 0;
}

template<class I, class T>
I knn_mutual(T* data, size_type nd, I* col_ind, size_type nc, I* row_ind, size_type nr, int k)
{
	I j=0;
	for(size_type r=0;r<nr;++r)
	{
		if( long(col_ind[r]) > long(row_ind[r]) )
		{
			I c = col_ind[r];
			if( long(c) < 0 ) c = I(-c);
			I* mc = find_mutual(col_ind+c*k, col_ind+(c+1)*k, row_ind[r]);
			/*if( r < 50 )
			{
				fprintf(stderr, "%d (%d): ", row_ind[r], c);
				for(I* beg1 = col_ind+c*k, *end1=col_ind+(c+1)*k;beg1 != end1;++beg1)
					fprintf(stderr, "%d, ", *beg1);
				fprintf(stderr, " -- %d\n", mc != 0);
			}*/
			if( mc != 0 )
			{
				(*mc) = -((*mc)+1);
				data[j] = data[r];
				col_ind[j] = col_ind[r];
				row_ind[j] = row_ind[r];
				++j;
			}
		}
		else if( long(col_ind[r]) < long(row_ind[r]) )
		{
			if( long(col_ind[r]) < 0 )
			{
				data[j] = data[r];
				col_ind[j] = -(col_ind[r]+1);
				row_ind[j] = row_ind[r];
				j++;
			}
		}
		else
		{
			data[j] = 0.0;
			col_ind[j] = col_ind[r];
			row_ind[j] = row_ind[r];
			j++;
		}

	}
	return j;
}


template<class I, class T>
void push_to_heap(T* dist2, size_type n, size_type m, T* data, size_type nd, I* col_ind, size_type nc, size_type offset, size_type k)
{
	typedef std::pair<T,I> index_dist;
	typedef std::vector< index_dist > index_vector;
#ifdef _OPENMP
	index_vector vheap(omp_get_max_threads()*k);
#else
	index_vector vheap(k);
#endif

	size_type m1=m;
	size_type n1=n;
	size_type t=m1*n1;

#	if defined(_OPENMP)
#	pragma omp parallel for
#	endif
	for(size_type r=0;r<n1;++r)
	{
		size_type rm = r*m;
		size_type rk = r*k;
#ifdef _OPENMP
		typename index_vector::iterator hbeg = vheap.begin()+omp_get_thread_num()*k, hcur=hbeg, hend=hbeg+k;
#else
		typename index_vector::iterator hbeg = vheap.begin(), hcur=hbeg, hend=hbeg+k;
#endif
		T* data_rk = data+rk;
		I* col_rk = col_ind+rk;
		//fprintf(stderr, "r: %d | data: %p - col: %p - hbeg: %p - dist2: %p\n", r, data_rk, col_rk, &(*hbeg), dist2);
		size_type c=0;
		//fprintf(stderr, "here-1 %ld -- %ld, %ld < %ld -- %ld, %ld < %ld\n", r, rm, rk, n*m1, k, offset, std::distance(hcur, hend));
		for(size_type l=std::min(k, offset);c<l;++c, ++hcur) *hcur = index_dist(data_rk[c], col_rk[c]);
		assert(hcur<=hend);
		for(;hcur != hend && c<m1;++c, ++hcur) *hcur = index_dist(dist2[rm+c], offset+c);
		assert(c==m || hcur == hend);
		if( hcur == hend ) std::make_heap(hbeg, hend);
		//fprintf(stderr, "here-2 %d\n", r);
		/*if ( r == 0)
		{
			if( std::min_element(hbeg, hend)->first > 0 )
				fprintf(stderr, "heap invalid-1: r(%d): %f (%d, %d) - offset: %d\n", r, std::min_element(hbeg, hend)->first, hcur == hend, c==m, offset);
		}*/
		for(;c<m1;++c)
		{
			assert((rm+c)<t);
			T d = dist2[rm+c];
			if( d < hbeg->first )
			{
				*hbeg = index_dist(d, offset+c);
				std::make_heap(hbeg, hend);
			}
		}
		//fprintf(stderr, "here-3 %d\n", r);
		/*if ( r == 0)
		{
			if( std::min_element(hbeg, hend)->first > 0 )
				fprintf(stderr, "heap invalid-2: r(%d): %f (%d, %d) - offset: %d\n", r, std::min_element(hbeg, hend)->first, hcur == hend, c==m, offset);
		}*/
		hcur = hbeg;
		for(c=0;c<k;++c, ++hcur)
		{
			assert(c<nc);
			data_rk[c] = hcur->first;
			col_rk[c] = hcur->second;
		}
		//fprintf(stderr, "here-4 %d\n", r);
	}
}

template<class I, class T>
void finalize_heap(T* data, size_type nd, I* col_ind, size_type nc, size_type offset, size_type k)
{
	typedef std::pair<T,I> index_dist;
	typedef std::vector< index_dist > index_vector;
#ifdef _OPENMP
	index_vector vheap(omp_get_max_threads()*k);
#else
	index_vector vheap(k);
#endif

	size_type e = size_type(T(nd)/k);

#	if defined(_OPENMP)
#	pragma omp parallel for
#	endif
	for(size_type r=0;r<e;++r)
	{
#ifdef _OPENMP
		typename index_vector::iterator hbeg = vheap.begin()+omp_get_thread_num()*k, hcur=hbeg, hend=hbeg+k;
#else
		typename index_vector::iterator hbeg = vheap.begin(), hcur=hbeg, hend=hbeg+k;
#endif
		T* data_rk = data+r*k;
		I* col_rk = col_ind+r*k;
		for(size_type c=0;c<k;++c, ++hcur) *hcur = index_dist(data_rk[c], col_rk[c]);
		std::sort_heap(hbeg, hbeg+k);
		hcur = hbeg;
		size_type c=0;
		if (hcur->second != I(r+offset)) // Ensure that the first neighbor is itself
		{
			assert(c<nc);
			data_rk[c] = 0;
			col_rk[c] = r+offset;
			c++;
		}
		for(;hcur != hend;++hcur)
		{
			if(hcur->second != I(r+offset) || c == 0)
			{
				assert(c<nc);
				data_rk[c] = hcur->first;
				col_rk[c] = hcur->second;
				++c;
				if( c == k ) break;
			}
		}
		if( c != k )
		{
			fprintf(stderr, "Bug for row: %ld -- %ld == %ld\n", r+offset, c, k);
			for(hcur=hbeg;hcur != hend;++hcur) fprintf(stderr, "%f - %ld\n", hcur->first, hcur->second);
			exit(1);
		}
	}
}

template<class I, class T>
I select_subset_csr(T* data, size_type nd, I* col_ind, size_type nc, I* row_ptr, size_type nr, I* selected, size_type scnt)
{
	nr-=1;
	I cnt = 0, rc=1;
	I* index_map = new I[nr];
	for(size_type i=0;i<nr;++i) index_map[i]=I(-1);
	for(size_type i=0;i<scnt;++i) index_map[selected[i]]=I(i);

	for(size_type s = 0;s<scnt;++s)
	{
		I r = selected[s];
		for(I j=row_ptr[r];j<row_ptr[r+1];++j)
		{
			if( index_map[col_ind[j]] != I(-1) )
			{
				data[cnt] = data[j];
				col_ind[cnt] = index_map[col_ind[j]];
				cnt ++;
			}
		}
		row_ptr[rc]=cnt;
		rc++;
	}
	delete[] index_map;
	return cnt;
}

template<class I, class T>
void self_tuning_gaussian_kernel_csr(T* sdist, size_type ns, T* data, size_type nd, I* col_ind, size_type nc, I* row_ptr, size_type nr)
{
	nr-=1;
	T* ndist = new T[nr];
#	ifdef _OPENMP
#	pragma omp parallel for
#	endif
	for(size_type i=0;i<nr;i++)
	{
		ndist[i] = 0;
	}
	for(size_type i=0;i<nr;i++)
	{
		if ( ndist[col_ind[i]] < data[i] )
			ndist[col_ind[i]] = data[i];
	}
	I* row_ind = new I[nc];
#	ifdef _OPENMP
#	pragma omp parallel for
#	endif
	for(size_type r=0;r<nr;++r)
	{
		for(I j=row_ptr[r];j<row_ptr[r+1];++j)
		{
			row_ind[j]=r;
		}
	}
#	ifdef _OPENMP
#	pragma omp parallel for
#	endif
	for(size_type i=0;i<nc;i++)
	{
		double den = 1.0;
		den *= std::sqrt(double(ndist[row_ind[i]]));
		den *= std::sqrt(double(ndist[col_ind[i]]));
		if( den != 0.0 ) sdist[i] = std::exp( -data[i] / T(den+1e-12) );
		else sdist[i] = std::exp( -data[i] );
	}
	delete[] ndist;
	delete[] row_ind;
}

template<class I, class T>
void normalize_csr(T* sdist, size_type ns, T* data, size_type nd, I* col_ind, size_type nc, I* row_ptr, size_type nr)
{
	nr-=1;
	T* ndist = new T[nr];
#	ifdef _OPENMP
#	pragma omp parallel for
#	endif
	for(size_type i=0;i<nr;i++)
	{
		ndist[i] = 0;
	}
	for(size_type i=0;i<nr;i++)
	{
		ndist[col_ind[i]] += data[i];
	}
#	ifdef _OPENMP
#	pragma omp parallel for
#	endif
	for(size_type i=0;i<nr;i++)
	{
		ndist[i] = T(1.0) / (ndist[i]+1e-12);
	}
	I* row_ind = new I[nc];
#	ifdef _OPENMP
#	pragma omp parallel for
#	endif
	for(size_type r=0;r<nr;++r)
	{
		for(I j=row_ptr[r];j<row_ptr[r+1];++j) row_ind[j]=r;
	}
#	ifdef _OPENMP
#	pragma omp parallel for
#	endif
	for(size_type i=0;i<nc;i++)
	{
		sdist[i] = data[i]*ndist[row_ind[i]]*ndist[col_ind[i]];
	}
	delete[] ndist;
	delete[] row_ind;
}
