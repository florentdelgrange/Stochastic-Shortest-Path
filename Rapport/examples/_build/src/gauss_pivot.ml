(* Let a be the matrix. This function switches the line i with
 * the line j. *)
let line_switch a i j =
  let n = Array.length a in
  let swap x y m =
    a.(i).(m) <- y ;
    a.(j).(m) <- x
  in
  if i < n && j < n then
    for k = 0 to ((Array.length a.(0)) -1) do
      swap a.(i).(k) a.(j).(k) k
    done
  else
    failwith "parameters i and j must be < than the number of lines of a."

let copy_matrix m =
  let l = Array.length m in
  if l = 0 then m
  else
    let result = Array.make l m.(0) in
    for i = 0 to l - 1 do
      result.(i) <- Array.copy m.(i)
    done;
    result

let print a =
  for i = 0 to ((Array.length a) - 1) do
    for j = 0 to ((Array.length a.(0)) - 1) do
        Printf.printf "%f\t" a.(i).(j);
    done;
    Printf.printf "\n";
  done;;

let pivot a b i n =
  let swap_max x y max_found =
    b.(i) <- y ;
    b.(max_found) <- x
  in
  let rec max_line a i n current_line current_max =
    if current_line >= n then current_max
    else if
      (abs_float a.(current_max).(i)) < (abs_float a.(current_line).(i))
    then max_line a i n (current_line + 1) current_line
    else
      max_line a i n (current_line + 1) current_max
  in
  let max_found = max_line a i n i i in
  if max_found > i then(
    line_switch a i max_found ;
    swap_max b.(i) b.(max_found) max_found )

let echelon a b =
  let n = Array.length a in
  for i = 0 to (n - 1) do
    pivot a b i n;
    if a.(i).(i) <> 0. then(
      for j = (i + 1) to (n - 1) do
        let coef = a.(j).(i) /. a.(i).(i) in
        b.(j) <- b.(j) -. b.(i) *. coef;
        for k = i to (n - 1) do
          a.(j).(k) <- a.(j).(k) -. a.(i).(k) *. coef;
        done;
      done)
  done

let inversible a n =
  let rec test i =
    if i = n then true
    else if a.(i).(i) = 0. then false
    else test (i + 1)
  in
  test 0

let resolve a b =
  let n = Array.length a in
  let a' = copy_matrix a in
  let b' = Array.copy b in
  let rec sum_coef a line row sol =
    if row = line then 0.
    else
      sol.(row) *. a.(line).(row) +. (sum_coef a line (row - 1) sol)
  in
  echelon a' b' ;
  if inversible a n then
    let sol = Array.make n 0. in
    for i = 0 to (n - 1) do
      let j = n - 1 - i in
      if i = 0 then
        sol.(j) <- b'.(j) /. a'.(j).(j)
      else
        sol.(j) <- (b'.(j) -. (sum_coef a' j (n - 1) sol)) /. a'.(j).(j)
    done;
    sol
  else failwith "Your system is not resolvable."
